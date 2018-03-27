# coding: utf-8

import pandas as pd
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.sql import select
import re
from progress.bar import ShadyBar
import configparser
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
import time
import sys

if len(sys.argv) < 2:
    raise Exception("Expected more args, usage: %s excelfile.xlsx" % sys.argv)

importfile = sys.argv[1]

config = configparser.ConfigParser()
config.read('config.ini')

# init
db = create_engine(config['db']['connection_url'])
db.connect()
meta = MetaData(db)
meta.reflect()
table = meta.tables[config['db']['table_name']]

df = pd.read_excel(importfile)
bar = ShadyBar('', max=len(df), suffix = '%(index)d/%(max)d - %(percent).1f%% - elapsed %(elapsed_td)s - eta %(eta_td)s')

min_diff = timedelta(15)
csv_file = importfile + '.csv'
f = None

def do_select(name, name2):
    s = select([table]).where(table.c.entity.like('%' + str(name2) + '%' + str(name) + '%'))
    res = db.execute(s)
    return res

def is_ok(data):
    date_close_to_death = False
    date_diff = None
    try:
        data['article_date'] = data['article_date'].replace('xx', '01')
        date = datetime.strptime(data['article_date'], '%Y-%m-%d')
        date_diff = date - data['died_date']
        date_diff = abs(date_diff)
        date_close_to_death = date_diff < min_diff
    except Exception:
        pass

    to_check_names = [
     #   '(?<!\w)' + re.escape(data['firstname'][0]) + '.?\W+' + re.escape(data['lastname'])  + '(?!\w)',
        '(?<!\w)' + re.escape(data['firstname'])    + '\W+'   + re.escape(data['lastname'])  + '(?!\w)',
        '(?<!\w)' + re.escape(data['lastname'])     + '\W+'   + re.escape(data['firstname']) + '(?!\w)'
    ]

    for name in to_check_names:
        if re.search(name, data['entity']):
            return 99999 if date_diff == None else date_diff.days

    return False

maps = {
    "firstname": 'First Name',
    "lastname": 'Last Name',
    'NML': 'NML ID',
    'died_date': 'Died Date',
    'diedplace': 'Died Place',
}

def proc(res, row, idx):
    global maps, f, csv_file

    for r in res:
        data = {
                '_index': idx,
                'entity': r['entity'],
                'article_date': r['publish_date'],
                'title': r['title'],
                'pid': r['pid']
            }
        for k, v in maps.items():
            data[k] = row[v]

        try:
            d = is_ok(data)
            if (d):
                data['datediff'] = d
                df = pd.DataFrame([data]).set_index('_index')
                if f == None:
                    with open(csv_file, 'w') as f:
                        df.to_csv(f, header=True)
                    f = open(csv_file, 'a')
                else:
                    df.to_csv(f, header=False)
        except Exception:
            print('err for:')
            print(data)
            raise


def worker():
    global maps
    while True:
        (idx, row) = q.get()
        res = do_select(row[maps['firstname']], row[maps['lastname']])
        proc(res, row, idx)
        res = do_select(row[maps['lastname']], row[maps['firstname']])
        proc(res, row, idx)
        q.task_done()
        bar.next()


num_worker_threads = 10
q = Queue()

for i in range(num_worker_threads):
    t = Thread(target=worker)
    t.daemon = True
    t.start()



for row in df.iterrows():
    # do query
    q.put(row)

q.join()
if f:
    f.close()
bar.finish()
