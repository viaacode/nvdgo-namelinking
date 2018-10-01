# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser
from pythonmodules.mediahaven import MediaHaven
from lib.matcher import Rater
from pythonmodules.cache import LocalCacher
import logging

logging.basicConfig()

logger = logging.getLogger()
fh = logging.FileHandler('fill_in_scores.log')
fh.setLevel(logging.WARNING)
logger.addHandler(fh)


parser = ArgumentParser(description='Add/fill in scores in link tables')
parser.add_argument('table', help='Origin table')
parser.add_argument('start', type=int, nargs='?', help='start from')
args = parser.parse_args()

config = Config(section='db')
conn = psycopg2.connect(config['connection_url'])
cur = conn.cursor()
cur2 = conn.cursor()
with timeit('SELECT', 5000):
    q = 'select pid, nmlid from %s order by pid' % args.table
    if args.start:
        q += ' offset %d' % int(args.start)
    cur.execute(q)

mh = MediaHaven()
mh.set_cacher(LocalCacher(500))

# for idx, row in [[0, ['0000000v8c_19140203_0003', '86b7e9db-0285-475a-bbea-a516fb3a806f']]]:
for idx, row in enumerate(tqdm(cur, total=cur.rowcount)):
    try:
        rater = Rater(row[0], row[1], mh)
        rating = rater.ratings()
        if rating.total == 0:
            continue
        columns = [rating.total]
        columns.extend(row)
        cur2.execute('UPDATE ' + args.table + ' SET score=%s WHERE pid=%s AND nmlid=%s', columns)
        conn.commit()
    except Exception as e:
        logger.warning('exception for %s', row)
        logger.exception(e)

conn.commit()
cur.close()
cur2.close()
conn.close()

