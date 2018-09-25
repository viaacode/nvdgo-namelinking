# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser


parser = ArgumentParser(
    description='Migrate statuses between attestation_link tables (doesn\'t overwrite if a status already set)')
parser.add_argument('from_table', help='Origin table')
parser.add_argument('to_table', help='Target table')
args = parser.parse_args()

config = Config(section='db')
conn = psycopg2.connect(config['connection_url_live'])
cur = conn.cursor()
cur2 = conn.cursor()
with timeit('SELECT', 5000):
    cur.execute('select status, kind, extras, pid, nmlid from %s where status != 0 AND status != 4' % args.from_table)

for idx, row in enumerate(tqdm(cur, total=cur.rowcount)):
    cur2.execute('UPDATE ' + args.to_table +
                 ' SET status=%s, kind=%s, extras=%s WHERE pid=%s AND nmlid=%s AND status=0',
                 row)
    if idx % 10 == 0:
        with timeit('commit', 250):
            conn.commit()

conn.commit()
cur.close()
cur2.close()
conn.close()

