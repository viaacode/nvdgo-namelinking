# -*- coding: utf-8 -*-

from pythonmodules.mediahaven import MediaHaven
from pythonmodules.stanfordner import StanfordNER

from sqlalchemy import Table, MetaData, create_engine

from progress.bar import ShadyBar
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# init 
ner = StanfordNER()
mh = MediaHaven(config)

db = create_engine(config['db']['connection_url'])
db.connect()
meta = MetaData(db, reflect=True)
table = meta.tables[config['db']['table_name']]

data = mh.search('+(workflow:GMS) +(archiveStatus:on_tape)')
# data.set_length(500) # debugging

bar = ShadyBar('', max=len(data), suffix = '%(index)d/%(max)d - %(percent).1f%% - elapsed %(elapsed_td)s - eta %(eta_td)s')

# truncate table first
db.execute(table.delete())

for idx, item in enumerate(data):
    text = item['description']
    entities = ner.detect_entities(text, 20, set(['PERSON']))
    if len(entities) > 0:
        date = [i['value'] for i in item['mdProperties'] if i['attribute'] == 'carrier_date']
        date = date[0] if len(date) > 0 else '0000-00-00'
        rows = [{
            'id': idx,
            'entity': e['value'], 
            'entity_type': e['type'],
            'context': e['context'] if 'context' in e else '',
            'pid': item['externalId'],
            'publish_date': date, 
            'title': item['title']
        } for e in entities]
        db.execute(table.insert(), rows)
    bar.next()
bar.finish()

