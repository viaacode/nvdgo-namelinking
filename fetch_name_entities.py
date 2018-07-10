# -*- coding: utf-8 -*-

from pythonmodules.mediahaven import MediaHaven
from pythonmodules.ner import NERFactory, normalize

from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql.expression import func

from pythonmodules.config import Config
from tqdm import tqdm
from argparse import ArgumentParser

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = True


config = Config()
table_name = config['db']['table_name']
parser = ArgumentParser(description='Use NER to look for entities and save')
parser.add_argument('--debug', action='store_true', help='Show debug info')
parser.add_argument('--test-connection', action='store_true', help='Just do a connection test to MediaHaven')
parser.add_argument('--clear', action='store_true', help='Clear the table before inserting')
parser.add_argument('--continue', action='store_true', help='Continue from last inserted row')
parser.add_argument('--continue-from', help='Continue from row CONTINUE_FROM')
parser.add_argument('--table', help='The table to store the results in, default: %s' % table_name)
args = parser.parse_args()


mh = MediaHaven(config)

clear_db = args.clear

if args.test_connection:
    mh.refresh_token()
    print(type(mh.one()) is dict)
    exit()

db = create_engine(config['db']['connection_url'])
db.connect()
meta = MetaData(db, reflect=True)
if args.table:
    table_name = args.table
try:
    table = meta.tables[table_name]
except KeyError:
    raise FileNotFoundError('Couldnt find table "%s"' % table_name)

start = 0
if vars(args)['continue']:
    start = db.execute(func.max(table.c.doc_index)).scalar() + 1
elif args.continue_from:
    start = int(args.continue_from)
else:
    start = 0

data = mh.search('+(workflow:GMS) +(archiveStatus:on_tape)', start)

# data.set_length(500) # debugging

# truncate table first
if not args.debug and args.clear:
    logger.warning("Clearing table %s" % table_name)
    db.execute(table.delete())

ner = NERFactory().get()
for idx, item in tqdm(enumerate(data), total=len(data) - start):
    text = item['description']
    entities = ner.tag(text)
    # if args.debug:
    #     print(list(entities))
    date = [i['value'] for i in item['mdProperties'] if i['attribute'] == 'carrier_date']
    date = date[0] if len(date) > 0 else '0000-00-00'
    rows = [{
        'doc_index': idx + start,
        'entity': normalize(e[0]),
        'entity_full': e[0],
        'entity_type': e[1][0],
        'pid': item['externalId'],
        'index': text_index
    } for text_index, e in enumerate(entities) if e[1][0] != 'O']
    if args.debug:
        print('DEBUG: %s Write %d rows to %s' % (item['externalId'], len(rows), table_name))
        pass
        # print('\n'.join(['\t'.join([str(r) for r in rows])]))
    elif len(rows):
        db.execute(table.insert(), rows)
