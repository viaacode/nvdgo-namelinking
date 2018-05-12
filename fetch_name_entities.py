# -*- coding: utf-8 -*-

from pythonmodules.mediahaven import MediaHaven
from pythonmodules.ner import NERFactory, normalize

from sqlalchemy import Table, MetaData, create_engine

from progress.bar import ShadyBar
import configparser
from tqdm import tqdm

import sys



config = configparser.ConfigParser()
config.read('config.ini')

# init
ner = NERFactory().get()
mh = MediaHaven(config)

def has_arg(*args):
    args = [arg for arg in sys.argv if arg not in args]
    exists = len(args) != len(sys.argv)
    sys.argv = args
    return exists


debug = has_arg('--debug', '-d')
clear_db = has_arg('--clear')

if not debug:
    db = create_engine(config['db']['connection_url'])
    db.connect()
    meta = MetaData(db, reflect=True)
    table = meta.tables[config['db']['table_name']]

start = 0
if len(sys.argv) > 1:
   start = int(sys.argv[1])

data = mh.search('+(workflow:GMS) +(archiveStatus:on_tape)', start)
# data.set_length(500) # debugging

#bar = tqdm(total=len(data) - start) # ShadyBar('', max=len(data), suffix = '%(index)d/%(max)d - %(percent).1f%% - elapsed %(elapsed_td)s - eta %(eta_td)s')
#for i in range(start):
#    bar.next()

# truncate table first
if not debug and clear_db:
    db.execute(table.delete())

for idx, item in tqdm(enumerate(data), total=len(data) - start):
    text = item['description']
    entities = ner.tag(text)
    #if debug:
    #    print(list(entities))
    date = [i['value'] for i in item['mdProperties'] if i['attribute'] == 'carrier_date']
    date = date[0] if len(date) > 0 else '0000-00-00'
    rows = [{
        'id': idx + start,
        'entity': normalize(e[0]),
        'entity_full': e[0],
        'entity_type': e[1][0],
        'pid': item['externalId'],
        'index': text_index
    } for text_index, e in enumerate(entities) if e[1] != 'O']
    if debug:
        pass
        # print('\n'.join(['\t'.join([str(r) for r in rows])]))
    elif len(rows):
        db.execute(table.insert(), rows)
