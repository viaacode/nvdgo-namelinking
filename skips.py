from pythonmodules.config import Config
from pythonmodules.db import DB
from tqdm import tqdm
from pywebserver.pywebserver.settings import SKIPS


db = DB(Config(section='db')['connection_url'])
db.connect()

affected = 0
for skip in tqdm(SKIPS):
    print(skip + ': ', end='')
    q = 'UPDATE attestation_linksolr ' \
        'SET status = 4 ' \
        'WHERE %s ' \
        'AND status = 0' % (skip.replace('%', '%%'),)
    res = db.execute(q)
    affected += res.rowcount
    print(affected)

print('%d rows affected' % (affected,))

