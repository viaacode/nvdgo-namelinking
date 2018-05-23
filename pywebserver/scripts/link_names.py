# coding: utf-8

import configparser

from sqlalchemy import MetaData, create_engine, and_, func
from sqlalchemy.sql import select
from django.db import IntegrityError
from queue import Queue
from threading import Thread

from pythonmodules.namenlijst import Namenlijst
from pythonmodules.ner import normalize

from attestation.models import Link
from tqdm import tqdm


class Linker:
    q = None
    bar = None
    table = None
    counts = dict()
    max_distance = 5

    def __init__(self, num_worker_threads=10, counts_only=False, debug=False):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.db = create_engine(config['db']['connection_url'])
        self.db.connect()
        meta = MetaData(self.db)
        meta.reflect()
        self.table = meta.tables[config['db']['table_name']]

        self.counts_only = bool(counts_only)
        self.debug = bool(debug)

        self.q = Queue()

        for i in range(num_worker_threads):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def start(self, df):
        self.bar = tqdm(total=len(df)) # ShadyBar('', max=len(df), suffix=suffix)
        for row in enumerate(df):
            self.q.put(row)
        self.q.join()

    @staticmethod
    def process(res, row, idx):
        nmlid = row['_id']

        for r in res:
            try:
                entity = r[0] + ' ' + r[1]
                pid = r[2].strip()
                Link.objects.get_or_create(nmlid=nmlid, entity=entity, pid=pid, distance=r[3])
            except IntegrityError:
                pass
            except Exception as e:
                print('[%d] err for %s: %s' % (idx, nmlid, e))
                raise

    @staticmethod
    def namesfilter(name):
        # filter out names that contain < or > to prevent checking the incomplete names like <...>eau
        return '<' not in name and '>' not in name

    def get_results(self, firstnames, lastnames):
        try:
            if len(firstnames) == 0 or len(lastnames) == 0:
                return []

            t1 = self.table
            t2 = self.table.alias()

            results = []
            for name1 in firstnames:
                for name2 in lastnames:
                    if self.debug:
                        print("Check %s %s" % (name1, name2))
                    s = select([
                            t1.c.entity_full,
                            t2.c.entity_full,
                            t1.c.pid,
                            func.abs(t1.c.index - t2.c.index).label('distance')
                        ]).where(
                            and_(
                                t1.c.entity == name1,
                                t2.c.entity == name2,
                                t1.c.id == t2.c.id,
                                func.abs(t1.c.index - t2.c.index) < self.max_distance,
                                t1.c.index != t2.c.index
                            )
                        )
                    results.extend(self.db.execute(s))
            if self.debug and len(results):
                print(results)
            return results
        except Exception as e:
            print(e)

    def work(self, idx, row):
        if row['victim_type'] not in self.counts:
            self.counts[row['victim_type']] = dict(skipped=0, ok=0, alternatives=0, found=0)

        if len(row['familyname']) > 2 and len(row['surname']) > 2:
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
                res = self.get_results(firstnames, lastnames)
                if res is not None:
                    self.counts[row['victim_type']]['found'] += len(res)
                Linker.process(res, row, idx)
        else:
            self.counts[row['victim_type']]['skipped'] += 1

    def worker(self):
        while True:
            (idx, row) = self.q.get()
            self.work(idx, row)
            self.q.task_done()
            self.bar.update(1)


def run(*args):
    if 'counts' in args:
        print('Warning: will check counts only, will not attempt to do lookups!')

    if 'debug' in args:
        print('Warning: debug mode')

    document = {
        # "died_year": 1914
    }
    options = [
        # 'EXTEND_DIED_PLACE',
        # 'EXTEND_DIED_DATE'
    ]

    people = Namenlijst().findPerson(document=document, options=options)

    linking = Linker(10 if 'consecutive' not in args else 1, counts_only='counts' in args, debug='debug' in args)
    linking.start(people)
    print(linking.counts)
