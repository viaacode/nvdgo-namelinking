# coding: utf-8

import configparser

from sqlalchemy import Table, MetaData, create_engine, or_, and_, func
from sqlalchemy.sql import select
from django.db import IntegrityError
from progress.bar import ShadyBar
from queue import Queue
from threading import Thread

from pythonmodules.namenlijst import Namenlijst
from pythonmodules.ner import normalize

from attestation.models import Link

# from psqlextra.query import ConflictAction

class Linker:
    f = None
    q = None
    bar = None
    write_count = 0
    table = None

    def __init__(self, num_worker_threads=10, csv_file=None):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.db = create_engine(config['db']['connection_url'])
        self.db.connect()
        meta = MetaData(self.db)
        meta.reflect()
        self.table = meta.tables[config['db']['table_name']]

        self.q = Queue()

        for i in range(num_worker_threads):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def start(self, df):
        suffix = '%(index)d/%(max)d - %(percent).1f%% - elapsed %(elapsed_td)s - eta %(eta_td)s'
        self.bar = ShadyBar('', max=len(df), suffix=suffix)
        for row in enumerate(df):
            self.q.put(row)
        self.q.join()
        self.bar.finish()

    @staticmethod
    def process(res, row, idx):
        nmlid = row['_id']

        for r in res:
            try:
                entity = r[0] + ' ' + r[1]
                pid = r[2].strip()
                Link.objects.get_or_create(nmlid=nmlid, entity=entity, pid=pid)
                    # on_conflict(['pid', 'nmlid'], ConflictAction.NOTHING).insert(...)
            except IntegrityError as e:
                pass
            except Exception as e:
                print('err for %s: %s' % (nmlid, e))
                raise

    @staticmethod
    def namesfilter(name):
        # filter out names that contain < or > to prevent checking the incomplete names like <...>eau
        return '<' not in name and '>' not in name

    def get_results(self, firstnames, lastnames):
        try:
            firstnames = filter(Linker.namesfilter, firstnames)
            lastnames = filter(Linker.namesfilter, lastnames)
            firstnames = map(lambda n: n.split(' ')[0], firstnames) # only use first first name

            firstnames = set(name for name in map(normalize, firstnames) if len(name) > 1)
            lastnames = set(name for name in map(normalize, lastnames) if len(name) > 1)
            if len(firstnames) == 0 or len(lastnames) == 0:
                return []

            t1 = self.table
            t2 = self.table.alias()

            results = []
            for name1 in firstnames:
                for name2 in lastnames:
                    # print("Check %s %s" % (name1, name2))
                    s = select([t1.c.entity_full, t2.c.entity_full, t1.c.pid]).where(
                        and_(
                            t1.c.entity == name1,
                            t2.c.entity == name2,
                            t1.c.id == t2.c.id,
                            func.abs(t1.c.index - t2.c.index) < 5,
                            t1.c.index != t2.c.index
                        )
                    )
                    results.extend(self.db.execute(s))
            # print('Query %s\n' % str(s))
            # if len(results):
            #     print(results)
            return results
        except Exception as e:
            print(e)

    def worker(self):
        while True:
            (idx, row) = self.q.get()
            # example row =
            # {
            #    'project_memberships':[
            #
            #    ],
            #    'surname':'<...>d',
            #    'cwxrm_remembered':False,
            #    'died_month':None,
            #    'memorials':[
            #       '06666349-f74b-4240-bd0b-1964782d259c'
            #    ],
            #    'died_day':None,
            #    'died_age':0,
            #    'born_month':None,
            #    'relations':[
            #
            #    ],
            #    'born_year':None,
            #    'war_casualty':True,
            #    'description':'',
            #    'died_year':None,
            #    'in_namelist':True,
            #    'alternative_familynames':[
            #
            #    ],
            #    'nationality':'',
            #    'sort_born_date':'',
            #    'alternative_surnames':[
            #
            #    ],
            #    'sort_died_date':'',
            #    'gender':'MALE',
            #    'familyname':'<...>ureux',
            #    'victim_type_details':'NONE',
            #    'born_day':None,
            #    '_id':'6f4b551c-a7c5-4941-bd5d-7ebd8db75c85',
            #    'victim_type':'MILITARY',
            #    'initials':''
            # }
            if len(row['familyname']) > 2 and len(row['surname']) > 2:
                lastnames = row['alternative_familynames']
                firstnames = row['alternative_surnames']
                firstnames.append(row['surname'])
                lastnames.append(row['familyname'])

                res = self.get_results(firstnames, lastnames)
                Linker.process(res, row, idx)

            self.q.task_done()
            self.bar.next()


document = {
    # "died_year": 1914
}
options = [
    # 'EXTEND_DIED_PLACE',
    # 'EXTEND_DIED_DATE'
]
people = Namenlijst().findPerson(document=document, options=options)
l = Linker(10)
l.start(people)
