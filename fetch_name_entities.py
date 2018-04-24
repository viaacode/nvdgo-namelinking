# -*- coding: utf-8 -*-

from pythonmodules.mediahaven import MediaHaven
from pythonmodules.ner import NERFactory

from sqlalchemy import Table, MetaData, create_engine

from progress.bar import ShadyBar
import configparser

import sys

config = configparser.ConfigParser()
config.read('config.ini')

# init
ner = NERFactory().get()
mh = MediaHaven(config)

args = [arg for arg in sys.argv if arg not in ('--debug', '-d')]
debug = len(args) != len(sys.argv)
sys.argv = args

if not debug:
    db = create_engine(config['db']['connection_url'])
    db.connect()
    meta = MetaData(db, reflect=True)
    table = meta.tables[config['db']['table_name']]

start = 0
if (len(sys.argv) > 1):
   start = int(sys.argv[1])

data = mh.search('+(workflow:GMS) +(archiveStatus:on_tape)', start)
# data.set_length(500) # debugging

bar = ShadyBar('', max=len(data), suffix = '%(index)d/%(max)d - %(percent).1f%% - elapsed %(elapsed_td)s - eta %(eta_td)s')
for i in range(start):
    bar.next()

# truncate table first
#if not debug:
#    db.execute(table.delete())

for idx, item in enumerate(data):
    text = item['description']
    entities = ner.tag_entities(text)
    if len(entities) > 0:
        date = [i['value'] for i in item['mdProperties'] if i['attribute'] == 'carrier_date']
        date = date[0] if len(date) > 0 else '0000-00-00'
        rows = [{
            'id': idx + start,
            'entity': e['value'],
            'entity_type': e['type'],
            # v'context': e['context'] if 'context' in e else '',
            'pid': item['externalId'],
            'publish_date': date,
            'title': item['title']
        } for e in entities]
        if debug:
            print('\n'.join(['%s\t%s\t%s' % (r['pid'], r['entity'], r['entity_type']) for r in rows]))
        else:
            db.execute(table.insert(), rows)
    bar.next()
bar.finish()
