# coding: utf-8

import pandas as pd
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.sql import select
from sqlalchemy import or_
import re
from progress.bar import ShadyBar
import configparser
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
import time
import sys
import numpy as np
from pythonmodules.namenlijst import Namenlijst

importfile = None
if len(sys.argv) >= 2:
    importfile = sys.argv[1]
else:
    raise Exception("Expected more args, usage: %s excelfile.xlsx" % sys.argv)


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
# df = df[(df['First Name'] == 'Armand') & (df['Last Name'] == 'Dubois')]
# df = df[(df['Last Name'] == 'Stevigny')]

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

    def __init__(self, num_worker_threads = 10):
        self.max_time_diff = timedelta(15)
        self.csv_file = 'test.csv'

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
            # print(str(idx) + ' ' + row['First Name'])
            data = {
                    '_index': idx,
                    'entity': r['entity'],
                    'article_date': r['publish_date'],
                    'title': r['title'],
                    'pid': r['pid']
                }
            for k, v in self.maps.items():
                data[k] = row[v]

            try:
                d = self.is_matching(data)
                if (d):
                    data['datediff'] = d
                    df = pd.DataFrame([data]).set_index('_index')
                    df.to_csv(self.f, header=(self.write_count == 0))
                    self.write_count += 1
            except Exception:
                print('err for:')
                print(data)
                raise

    def is_matching(self, data):
        date_close_to_death = False
        date_diff = None
        try:
            data['article_date'] = data['article_date'].replace('xx', '01')
            date = datetime.strptime(data['article_date'], '%Y-%m-%d')
            date_diff = date - data['died_date']
            date_diff = abs(date_diff)
            date_close_to_death = date_diff < self.max_time_diff
        except Exception:
            pass

        firstnames = data['firstname'].split(' ')
        for k, v in enumerate(firstnames):
            if k > 0:
                firstnames[k] = '(\W+' + re.escape(v) + ')?'
            else:
                firstnames[k] = re.escape(v)

        firstnames = ''.join(firstnames)

        to_check_names = [
         #   '(?<!\w)' + re.escape(data['firstname'][0]) + '.?\W+' + re.escape(data['lastname'])  + '(?!\w)',
            '(?<!\w)' + firstnames + '\W+' + re.escape(data['lastname'])  + '(?!\w)',
            '(?<!\w)' + re.escape(data['lastname']) + '\W+' + firstnames + '(?!\w)'
        ]

        for name in to_check_names:
            if re.search(name, data['entity'], re.IGNORECASE):
                return 99999 if date_diff == None else date_diff.days

        return False

    def get_results(self, name1, name2):
        try:
            s = select([self.table]).where(or_(
                self.table.c.entity.like('%' + str(name2) + '%' + str(name1) + '%'),
                self.table.c.entity.like('%' + str(name1) + '%' + str(name2) + '%')
                )
            )
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


l = Linker(10)
l.start(df)
