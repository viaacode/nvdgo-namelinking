# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser
import logging

logger = logging.getLogger(__name__)
parser = ArgumentParser(
    description='Migrate statuses between attestation_link tables (doesn\'t overwrite if a status already set)')
parser.add_argument('from_table', help='Origin table')
parser.add_argument('to_table', help='Target table')
parser.add_argument('--debug', action='store_true', default=False, help='Show debug log messages')
args = parser.parse_args()
logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

config = Config(section='db')
conn = psycopg2.connect(config['connection_url'])
cur = conn.cursor()
cur2 = conn.cursor()
with timeit('SELECT', 5000):
    cur.execute('select status, kind, extras, pid, nmlid from %s where status != 0 AND status != 4' % args.from_table)

processed = 0
total = cur.rowcount
q = 'UPDATE ' + args.to_table + ' SET status=%s, kind=%s, extras=%s WHERE pid=%s AND nmlid=%s AND status=0'
for idx, row in enumerate(tqdm(cur, total=total)):
    res = cur2.execute(q, row)
    processed += cur2.rowcount
    logger.debug('%d changed for: %s', cur2.rowcount, row)
    if idx % 10 == 0:
        with timeit('commit', 250):
            conn.commit()

conn.commit()
cur.close()
cur2.close()
conn.close()


print('%d of %d updated (%d%%)' % (processed, total, int(processed/total*100) if total != 0 else 0))
