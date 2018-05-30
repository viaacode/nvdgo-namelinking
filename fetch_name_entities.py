# -*- coding: utf-8 -*-

from pythonmodules.mediahaven import MediaHaven
from pythonmodules.ner import NERFactory, normalize

from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql.expression import func

import configparser
from tqdm import tqdm

import sys


def has_arg(*args):
    args = [arg for arg in sys.argv if arg not in args]
    exists = len(args) != len(sys.argv)
    sys.argv = args
    return exists


config = configparser.ConfigParser()
config.read('config.ini')

mh = MediaHaven(config)

debug = has_arg('--debug', '-d')
clear_db = has_arg('--clear')

if has_arg('--test-connection'):
    mh.refresh_token()
    print(type(mh.one()) is dict)
    exit()

if not debug:
    db = create_engine(config['db']['connection_url'])
    db.connect()
    meta = MetaData(db, reflect=True)
    table = meta.tables[config['db']['table_name']]

start = 0
if len(sys.argv) > 1:
    if sys.argv[1] in ['--continue', '-c']:
        start = db.execute(func.max(table.c.id)).scalar() + 1
    else:
        start = int(sys.argv[1])

data = mh.search('+(workflow:GMS) +(archiveStatus:on_tape)', start)

# data.set_length(500) # debugging

# truncate table first
if not debug and clear_db:
    db.execute(table.delete())

ner = NERFactory().get()
for idx, item in tqdm(enumerate(data), total=len(data) - start):
    text = item['description']
    entities = ner.tag(text)
    # if debug:
    #     print(list(entities))
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
