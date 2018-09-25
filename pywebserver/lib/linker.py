# coding: utf-8

import configparser

from sqlalchemy import MetaData, create_engine, and_
from sqlalchemy.sql import select
from queue import Queue
from threading import Thread
from django.db import IntegrityError
from pythonmodules.decorators import classcache
from pythonmodules.config import Config
from pythonmodules.cache import LocalCacher

from pysolr import Solr

import attestation.models as models
from more_itertools import chunked

from pythonmodules.profiling import timeit

from tqdm import tqdm
import logging

from pythonmodules.namenlijst import Namenlijst, Conversions
import pandas as pd
from .helpers import AttributeMapper, RowWrapper


def namenlijst(**kwargs):
    # def wrap(n):
    #    return AttributeMapper(n, dict(firstname='surname', lastname='familyname'))
    wrap = lambda k: AttributeMapper(k, dict(firstname='surname', lastname='familyname'))
    return RowWrapper(Namenlijst().findPerson(**kwargs), wrap)


def kunstenaars(**kwargs):
    people = pd.read_excel('datasources/20180605_kunstenaars_IFFM.xlsx')
    people = [{
                "firstname": r[0].split()[0],
                "lastname": ' '.join(r[0].split()[1:]), "_id": n,
                "victim_type": "kunstenaar"
              } for n, r in enumerate(people.iterrows())]
    return people


Datasources = {
    "kunstenaars": {
        "func": kunstenaars,
        'table': 'LinkKunstenaars'
    },
    "namenlijst": {
        "func": namenlijst,
        'table': 'LinkNamenlijst'
    }
}


class Linker:
    counts = dict()
    max_distance = 2
    skip_if_higher_than_count = 200
    to_skip = []

    def __init__(self, num_worker_threads=10, counts_only=False, no_skips=False, no_write=False, categorizer=None,
                 table=None):
        self.bar = None
        self.categorizer = categorizer if categorizer is not None else 'victim_type'
        self.__cacher = LocalCacher(200)
        self.log = logging.getLogger(__name__)
        config = Config()
        if table is None:
            table = 'Link'
        self.link = models.__dict__[table]

        self.log.debug("Will write to %s '%s'" % (table, str(self.link)))
        self._solr = Solr(config['wordsearcher']['solr'])
        self.db = create_engine(config['db']['connection_url'])
        self.db.connect()
        # meta = MetaData(self.db)
        # meta.reflect()
        # self.table = meta.tables[config['db']['table_name']]

        if not no_skips:
            self.to_skip = set(models.Link.objects.filter(status=models.Link.SKIP)
                                           .order_by('nmlid').values_list('nmlid', flat=True)
                                           .distinct())

        # quick hack to write skips to csv
        #
        # with open('skips.csv', 'w+') as f:
        #     f.write('nmlid,name\n')
        #     for nmlid in tqdm(self.to_skip):
        #         nml = Namenlijst()
        #         p = nml.findPerson(document={"_id": nmlid}, limit=1)
        #         err = False
        #         try:
        #             p = next(p)
        #         except StopIteration:
        #             name = '[NOTFOUND]'
        #             err = True
        #         if not err:
        #             name = '%s, %s' % (p['familyname'], p['surname'])
        #         f.write('%s,"%s"\n' % (nmlid, name))
        # exit()

        self.counts_only = bool(counts_only)
        self.no_write = bool(no_write)
        self.log.info('found %d nmlids to skip' % len(self.to_skip))

        self.q = Queue()

        for i in range(num_worker_threads):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def start(self, df, initial=0):
        self.bar = tqdm(total=len(df), initial=initial)
        for row in enumerate(df):
            self.q.put(row)
        self.q.join()

    def process(self, res, row, idx):
        nmlid = row['_id']
        values = (self.link(nmlid=nmlid, pid=r[0].strip(), entity=' '.join(r[1:])) for r in res)
        self.link.objects.bulk_create(values)
        return

    @staticmethod
    def namesfilter(name):
        # filter out names that contain < or > to prevent checking the incomplete names like <...>eau
        return '<' not in name and '>' not in name

    def clear(self):
        with timeit('Clearing model %s' % self.link._meta.db_table):
            # this doesnt reset identity and is slower...
            # self.link.objects.all().delete()
            self.db.execute('TRUNCATE TABLE %s RESTART IDENTITY' % self.link._meta.db_table)

    def get_cacher(self):
        return self.__cacher

    def get_links(self, names):
        res = self._solr.search(r'text:"\"%s\""~1' % r'\") (\"'.join(names), rows=100000, fl='id')
        if not len(res):
            return []
        name = ' '.join(names)
        return [(item['id'], name) for item in res.docs]

    # @classcache
    def get_links_old(self, names):
        # conditions = []
        #
        # self.log.debug("Check %s" % str(names))
        # conditions.append(self.table.c.entity == max(names, key=len))
        #
        # for name in names:
        #     alias = self.table.alias()
        #     # selects.append(alias)
        #     conditions.append(self.table.c.doc_index.in_(
        #         select([alias.c.doc_index]).where(alias.c.entity == name)
        #     ))
        #
        # docids = select([self.table.c.doc_index]).where(and_(*conditions)).distinct()
        # with timeit('slow pre-select for "%s"' % (' '.join(names)), 1000):
        #     docids = [a[0] for a in self.db.execute(docids).fetchall()]
        #
        # if not len(docids):
        #     return []
        #
        # print('docids: %d' % len(docids))
        #
        results = []
        # for ids in chunked(docids, 100):
        selects = [self.table.c.pid]
        conditions = []
        # conditions = [self.table.c.doc_index.in_(ids)]
        joins = []
        prevalias = None
        alias = self.table

        for name in names:
            if prevalias is not None:
                distances = [prevalias.c.index - i for i in range(1, self.max_distance)]
                distances.extend([prevalias.c.index + i for i in range(1, self.max_distance)])
                joins.append((alias, and_(self.table.c.doc_index == alias.c.doc_index, alias.c.index.in_(distances))))
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
            results.extend([tuple(row) for row in self.db.execute(s).fetchall()])

        return results

    def get_results(self, nmlid, firstnames, lastnames):
        try:
            if len(firstnames) == 0 or len(lastnames) == 0:
                self.log.info('Empty first- or lastnames')
                return set()

            results = set()

            for fname in firstnames:
                for lname in lastnames:
                    self.log.debug('"%s" "%s"' % (fname, lname))

            allnames = [fname + ' ' + lname for fname in firstnames for lname in lastnames]
            # allnames.extend([
            #                   lname + ' ' + fname
            #                   for fname in firstnames
            #                   for lname in lastnames
            #                   if ' ' in lname or ' ' in fname  # optim: no need to check reverse order
            #                                                    #  if only 2 words in total
            #                 ])

            allnames = sorted(allnames, key=len, reverse=True)
            for names in allnames:
                rows = self.get_links(names.split(' '))
                if len(rows):
                    self.log.debug("%s, check: %s: %d results", nmlid, names, len(rows))
                    results = results.union(rows)
            return results
        except Exception as e:
            self.log.exception(e)
            return set()

    def work(self, idx, row):
        if row[self.categorizer] not in self.counts:
            self.counts[row[self.categorizer]] = dict(skipped=0, ok=0, alternatives=0, found=0, skipped_too_freq=0)

        if len(row['firstname']) <= 2 or len(row['lastname']) <= 2:
            self.counts[row[self.categorizer]]['skipped'] += 1
            return

        if row['_id'] in self.to_skip:
            self.counts[row[self.categorizer]]['skipped_too_freq'] += 1
            return

        names = Conversions.get_names(row, Linker.namesfilter)

        # # use first first name and first 2 firstnames
        # fnames = []
        # for name in names.firstnames_normalized:
        #     names = name.split(' ')
        #     if len(names) > 1:
        #         fnames.extend([names[0], names[0] + ' ' + names[1]])
        #     else:
        #         fnames.append(name)

        # firstnames = set(fnames)

        # remove single letter words such as 't' for eg. "edmond t kint de roodenbeke"
        # lastnames = set(' '.join((l for l in lastname.split(' ') if len(l) > 1)) for lastname in lastnames)

        if len(names.firstnames_normalized) == 0 or len(names.lastnames_normalized) == 0:
            self.counts[row[self.categorizer]]['skipped'] += 1
        else:
            self.counts[row[self.categorizer]]['ok'] += 1
            self.counts[row[self.categorizer]]['alternatives'] += len(names.firstnames_normalized) * \
                                                                  len(names.lastnames_normalized) - 1

        if not self.counts_only:
            res = self.get_results(row['_id'], names.firstnames_normalized, names.lastnames_normalized)
            if len(res):
                self.counts[row[self.categorizer]]['found'] += len(res)
                self.process(res, row, idx)

    def worker(self):
        while True:
            (idx, row) = self.q.get()
            try:
                self.work(idx, row)
            except Exception as e:
                self.log.exception(e)
            self.q.task_done()
            self.bar.update(1)

