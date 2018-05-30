# coding: utf-8

import configparser

from sqlalchemy import MetaData, create_engine, and_, func
from sqlalchemy.sql import select
from queue import Queue
from threading import Thread

from pythonmodules.namenlijst import Namenlijst
from pythonmodules.ner import normalize

from attestation.models import Link
from tqdm import tqdm
import logging


class Linker:
    q = None
    bar = None
    table = None
    counts = dict()
    max_distance = 2
    skip_if_higher_than_count = 200
    to_skip = []

    def __init__(self, num_worker_threads=10, counts_only=False, no_skips=False):
        self.log = logging.getLogger('link_names')
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.db = create_engine(config['db']['connection_url'])
        self.db.connect()
        meta = MetaData(self.db)
        meta.reflect()
        self.table = meta.tables[config['db']['table_name']]

        if not no_skips:
            to_skip_query = '''
            select 
                max(b.entity), res.id, max(res.c) as linkscount 
            from 
                (select 
                    count(a.id) as c, a.nmlid as id   
                from attestation_link a
                group by a.nmlid
                having count(a.id) > %d
                order by c desc) as res,
                attestation_link b
            where res.id = b.nmlid
            group by res.id
            order by linkscount DESC
            ''' % self.skip_if_higher_than_count

            self.to_skip = [row[1] for row in self.db.execute(to_skip_query)]

        self.counts_only = bool(counts_only)
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
                if not Link.objects.filter(**uq).exists():
                    Link.objects.create(**uq)
            except Exception as e:
                self.log.error('[%d] err for %s: %s' % (idx, nmlid, e))

    @staticmethod
    def namesfilter(name):
        # filter out names that contain < or > to prevent checking the incomplete names like <...>eau
        return '<' not in name and '>' not in name

    def get_results(self, nmlid, firstnames, lastnames):
        try:
            if len(firstnames) == 0 or len(lastnames) == 0:
                return set()

            results = set()
            for name1 in firstnames:
                for name2 in lastnames:
                    tables = [self.table]
                    selects = [tables[0].c.pid, tables[0].c.entity_full]
                    conditions = [tables[0].c.entity == name1]
                    prevalias = tables[0]
                    for word in name2.split(' '):
                        alias = self.table.alias()
                        tables.append(alias)
                        selects.append(alias.c.entity_full)
                        # selects.append(func.abs(prevalias.c.index - alias.c.index).label('distance'))
                        conditions.append(alias.c.entity == word)
                        conditions.append(prevalias.c.id == alias.c.id)
                        conditions.append(func.abs(prevalias.c.index - alias.c.index) < self.max_distance)
                        conditions.append(prevalias.c.index != alias.c.index)
                        prevalias = alias

                    s = select(selects).where(and_(*conditions))
                    rows = [tuple(row) for row in self.db.execute(s).fetchall()]
                    self.log.debug("%s, check: %s %s, %d results", nmlid, name1, name2, len(rows))
                    if len(rows):
                        results = results.union(rows)
            if len(results):
                self.log.debug(results)
            return set(results)
        except Exception as e:
            self.log.error(e)
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
        firstnames = map(lambda n: n.split(' ')[0], firstnames)  # only use first first name

        firstnames = set(name for name in map(normalize, firstnames) if len(name) > 1)
        lastnames = set(name for name in map(normalize, lastnames) if len(name) > 1)

        if len(firstnames) == 0 or len(lastnames) == 0:
            self.counts[row['victim_type']]['skipped'] += 1
        else:
            self.counts[row['victim_type']]['ok'] += 1
            self.counts[row['victim_type']]['alternatives'] += len(firstnames) * len(lastnames) - 1

        if not self.counts_only:
            res = self.get_results(row['_id'], firstnames, lastnames)
            if res is not None:
                self.counts[row['victim_type']]['found'] += len(res)
            self.process(res, row, idx)

    def worker(self):
        while True:
            (idx, row) = self.q.get()
            self.work(idx, row)
            self.q.task_done()
            self.bar.update(1)


class GeneratorLimit(object):
    def __init__(self, gen, limit):
        self.gen = gen
        self.limit = limit

    def __len__(self):
        return self.limit

    def __iter__(self):
        return (next(self.gen) for i in range(self.limit))


def run(*args):
    logger = logging.getLogger('link_names')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler('link_names.log'))
    logger.info('running with arguments: %s' % (' "%s"' * len(args)), *args)

    if 'counts' in args:
        logger.info('will check counts only, will not attempt to do lookups!')

    if 'debug' in args:
        logger.info('debug mode')
        logger.setLevel(logging.DEBUG)

    if 'consecutive' in args:
        logger.info('will not run in parallel')

    if 'no-skips' in args:
        logger.info('will not skip frequent names')

    if 'debug-sql' in args:
        logger.info('will show some sql debug info')
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    document = {
        # '_id': '4a7795fd-6fa0-4dc3-bcc3-4ee82c371077'
        # "died_year": 1914
    }
    options = [
        # 'EXTEND_DIED_PLACE',
        # 'EXTEND_DIED_DATE'
    ]

    people = Namenlijst().findPerson(document=document, options=options)

    if len(args) and args[0].isdigit():
        logger.info('will only do first %s' % args[0])
        if len(people) > int(args[0]):
            people = GeneratorLimit(people, int(args[0]))

    linking = Linker(5 if 'consecutive' not in args else 1,
                     counts_only='counts' in args,
                     no_skips='no-skips' in args)
    linking.start(people)
    logger.info(linking.counts)
