# coding: utf-8

import configparser

from sqlalchemy import MetaData, create_engine, and_, func
from sqlalchemy.sql import select
from queue import Queue
from threading import Thread
from django.db import IntegrityError
from pythonmodules.ner import normalize
from pythonmodules.decorators import classcache
from pythonmodules.cache import LocalCacher

from attestation.models import LinkNew as Link, Link as LinkForSkips

from pythonmodules.profiling import timeit

from tqdm import tqdm
import logging


class Linker:
    counts = dict()
    max_distance = 2
    skip_if_higher_than_count = 200
    to_skip = []

    def __init__(self, num_worker_threads=10, counts_only=False, no_skips=False, no_write=False):
        self.bar = None
        self.__cacher = LocalCacher(200)
        self.log = logging.getLogger('link_names')
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.db = create_engine(config['db']['connection_url'])
        self.db.connect()
        meta = MetaData(self.db)
        meta.reflect()
        self.table = meta.tables[config['db']['table_name']]

        if not no_skips:
            self.to_skip = set(LinkForSkips.objects.filter(status=LinkForSkips.SKIP)
                                           .order_by('nmlid').values_list('nmlid', flat=True)
                                           .distinct())

        self.counts_only = bool(counts_only)
        self.no_write = bool(no_write)
        self.log.info('found %d nmlids to skip' % len(self.to_skip))

        self.q = Queue()

        for i in range(num_worker_threads):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def start(self, df):
        self.bar = tqdm(total=len(df))
        for row in enumerate(df):
            self.q.put(row)
        self.q.join()

    def process(self, res, row, idx):
        nmlid = row['_id']

        for r in res:
            try:
                pid = r[0].strip()
                entity = ' '.join(r[1:])
                uq = dict(nmlid=nmlid, entity=entity, pid=pid)
                self.log.debug(uq)
                # if not Link.objects.filter(**uq).exists():
                if not self.no_write:
                    with timeit('slow create %s' % str(uq), 200):
                        Link.objects.create(**uq)
            except IntegrityError:
                pass
            except Exception as e:
                self.log.exception('[%d] err for %s: %s' % (idx, nmlid, e))

    @staticmethod
    def namesfilter(name):
        # filter out names that contain < or > to prevent checking the incomplete names like <...>eau
        return '<' not in name and '>' not in name

    def get_cacher(self):
        return self.__cacher

    @classcache
    def get_links(self, names):
        selects = [self.table.c.pid]
        conditions = []
        joins = []
        prevalias = None
        alias = self.table
        # self.log.debug("Check %s" % str(names))

        for name in names:
            if prevalias is not None:
                distances = [prevalias.c.index - i for i in range(1, self.max_distance)]
                distances.extend([prevalias.c.index + i for i in range(1, self.max_distance)])
                joins.append((alias, and_(self.table.c.id == alias.c.id, alias.c.index.in_(distances))))
            selects.append(alias.c.entity_full)
            conditions.append(alias.c.entity == name)
            prevalias = alias
            alias = self.table.alias()

        with timeit('slow select for "%s"' % (' '.join(names)), 1000):
            s = select(selects)
            join = self.table
            for x in joins:
                join = join.join(*x)
            s = s.select_from(join)
            s = s.where(and_(*conditions))
            results = [tuple(row) for row in self.db.execute(s).fetchall()]

        return results

    def get_results(self, nmlid, firstnames, lastnames):
        try:
            if len(firstnames) == 0 or len(lastnames) == 0:
                return set()

            results = set()

            for fname in firstnames:
                for lname in lastnames:
                    self.log.debug('"%s" "%s"' % (fname, lname))

            allnames = [fname + ' ' + lname for fname in firstnames for lname in lastnames]
            allnames.extend([
                              lname + ' ' + fname
                              for fname in firstnames
                              for lname in lastnames
                              if ' ' in lname or ' ' in fname  # optim: no need to check reverse order
                                                               #  if only 2 words in total
                            ])

            for names in allnames:
                rows = self.get_links(names.split(' '))
                self.log.debug("%s, check: %s: %d results", nmlid, names, len(rows))
                if len(rows):
                    results = results.union(rows)
            return results
        except Exception as e:
            self.log.exception(e)
            return set()

    def work(self, idx, row):
        if row['victim_type'] not in self.counts:
            self.counts[row['victim_type']] = dict(skipped=0, ok=0, alternatives=0, found=0, skipped_too_freq=0)

        if len(row['familyname']) <= 2 or len(row['surname']) <= 2:
            self.counts[row['victim_type']]['skipped'] += 1
            return

        if row['_id'] in self.to_skip:
            self.counts[row['victim_type']]['skipped_too_freq'] += 1
            return

        lastnames = row['alternative_familynames']
        firstnames = row['alternative_surnames']
        firstnames.append(row['surname'])
        lastnames.append(row['familyname'])

        firstnames = filter(Linker.namesfilter, firstnames)
        lastnames = filter(Linker.namesfilter, lastnames)

        firstnames = set(name for name in map(normalize, firstnames) if len(name) > 1)
        lastnames = set(name for name in map(normalize, lastnames) if len(name) > 1)

        # use first first name and first 2 firstnames
        fnames = list()
        for name in firstnames:
            names = name.split(' ')
            if len(names) > 1:
                fnames.extend([names[0], names[0] + ' ' + names[1]])
            else:
                fnames.append(name)

        firstnames = set(fnames)

        # remove single letter words such as 't' for eg. "edmond t kint de roodenbeke"
        # lastnames = set(' '.join((l for l in lastname.split(' ') if len(l) > 1)) for lastname in lastnames)

        if len(firstnames) == 0 or len(lastnames) == 0:
            self.counts[row['victim_type']]['skipped'] += 1
        else:
            self.counts[row['victim_type']]['ok'] += 1
            self.counts[row['victim_type']]['alternatives'] += len(firstnames) * len(lastnames) - 1

        if not self.counts_only:
            res = self.get_results(row['_id'], firstnames, lastnames)
            if len(res):
                self.counts[row['victim_type']]['found'] += len(res)
            self.process(res, row, idx)

    def worker(self):
        while True:
            (idx, row) = self.q.get()
            self.work(idx, row)
            self.q.task_done()
            self.bar.update(1)

