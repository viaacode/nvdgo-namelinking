# coding: utf-8

import pandas as pd
import re
import configparser
import time
import sys
import numpy as np

from sqlalchemy import Table, MetaData, create_engine, or_, and_, func
from sqlalchemy.sql import select
from progress.bar import ShadyBar
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread

from pythonmodules.namenlijst import Namenlijst
from pythonmodules.archief import Archief
from pythonmodules.ner import normalize

importfile = None
if len(sys.argv) >= 2:
    importfile = sys.argv[1]
else:
    raise Exception("Expected more args, usage: %s excelfile.xlsx [outputfile.csv]" % sys.argv)


if importfile:
    df = pd.read_excel(importfile, converters = {'NML ID': str})
    # filter out some unnecessary results
    df.dropna(subset=['First Name', 'Last Name'], inplace=True)
    df = df[(df['First Name'].str.len() != 2) | ~(df['First Name'].str.endswith('.'))]
else:
    raise "TODO"
    nl = Namenlijst()
    df = nl.findPerson()

# for testing:
#df = df[(df['First Name'] == 'Armand') & (df['Last Name'] == 'Dubois')]
# df = df[(df['Last Name'] == 'Stevigny')]
#df = df[(df['First Name'] == 'Jean') & (df['Last Name'] == 'Robyn')]


class Linker:
    maps = {
        "firstname": 'First Name',
        "lastname": 'Last Name',
        'NML': 'NML ID',
        'died_date': 'Died Date',
        'diedplace': 'Died Place',
    }
    f = None
    q = None
    bar = None
    write_count = 0
    table = None

    def __init__(self, num_worker_threads = 10, csv_file = None):
        self.max_time_diff = timedelta(15)
        self.csv_file = 'test.csv' if csv_file is None else csv_file

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
        self.bar = ShadyBar('', max=len(df), suffix = '%(index)d/%(max)d - %(percent).1f%% - elapsed %(elapsed_td)s - eta %(eta_td)s')
        self.f = open(self.csv_file, 'a')
        for row in df.iterrows():
            self.q.put(row)
        self.q.join()
        if self.f:
            self.f.close()
        self.bar.finish()
        print(str(self.write_count) + ' results found')

    def process(self, res, row, idx):
        for r in res:
            data = {
                    'entity': r[0] + ' ' + r[1],
                    'pid': r[2].strip()
                }
            for k, v in self.maps.items():
                data[k] = str(row[v])

            try:
                data = dict(
                    archief_url = Archief.pid_to_url(data['pid'], data['entity']),
                    namenlijst_url = 'https://database.namenlijst.be/#/person/_id=' + data['NML'],
                    **data
                )
                if (self.write_count == 0):
                    self.f.write(','.join(data.keys()) + '\n')
                self.f.write('"' + '","'.join([val.replace('"', '""') for val in data.values()]) + '"\n')
                self.write_count += 1
            except Exception:
                print('err for:')
                print(data)
                raise

    def get_results(self, name1, name2):
        try:
            name1 = normalize(name1)
            name2 = normalize(name2)
            t1 = self.table
            t2 = self.table.alias()
            s = select([t1.c.entity_full, t2.c.entity_full, t1.c.pid]).where(
                        and_(
                            t1.c.entity == name1,
                            t2.c.entity == name2,
                            t1.c.id == t2.c.id,
                            func.abs(t1.c.index - t2.c.index) < 5
                        )
                    )
            # print('Query %s\n' % str(s))
            return self.db.execute(s)
        except Exception as e:
            print(e)

    def worker(self):
        maps = self.maps
        while True:
            (idx, row) = self.q.get()
            if (row[maps['firstname']] and row[maps['lastname']]):
                firstname = row[maps['firstname']].split(' ')[0]
                res = self.get_results(firstname, row[maps['lastname']])
                self.process(res, row, idx)
            self.q.task_done()
            self.bar.next()
            self.f.flush()

l = Linker(10, csv_file = sys.argv[2])
l.start(df)
