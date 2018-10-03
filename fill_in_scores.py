# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser
from pywebserver.lib.matcher import Rater
import logging
from pythonmodules.multithreading import multithreaded


parser = ArgumentParser(description='Add/fill in scores in link tables')
parser.add_argument('--start', type=int, nargs='?', help='start from')
parser.add_argument('--table', help='Origin table', default='attestation_linksolr2')
parser.add_argument('--limit', type=int, help='limit amount done')
parser.add_argument('--clear-log-file', default=False, action='store_true', help='Empty the log file first')
parser.add_argument('--log-file', type=str, default='fill_in_scores.log', help='Set log file name')
args = parser.parse_args()

if args.clear_log_file:
    open(args.log_file, 'w').close()

logging.basicConfig()
logger = logging.getLogger()
fh = logging.FileHandler(args.log_file)
fh.setLevel(logging.INFO)
logger.addHandler(fh)


config = Config(section='db')
conn = psycopg2.connect(config['connection_url'])
conn2 = psycopg2.connect(config['connection_url'])
cur = conn.cursor()
with timeit('SELECT', 5000):
    q = 'SELECT pid, nmlid FROM %s ORDER BY pid' % args.table
    if args.limit:
        q += ' LIMIT %d' % int(args.limit)
    if args.start:
        q += ' OFFSET %d' % int(args.start)
    cur.execute(q)


@multithreaded(10, pre_start=True, pass_thread_id=False)
def process(row):
    try:
        rater = Rater(row[0], row[1])
        rating = rater.ratings()
        if rating.total == 0:
            return
        columns = [rating.total]
        columns.extend(row)
        cur2 = conn2.cursor()
        cur2.execute('UPDATE ' + args.table + ' SET score=%s WHERE pid=%s AND nmlid=%s', columns)
        cur2.close()
        conn2.commit()
    except Exception as e:
        logger.warning('exception for %s', row)
        logger.exception(e)


process._multithread.pbar = tqdm(total=cur.rowcount)
process(cur)

conn.commit()
cur.close()
conn.close()
conn2.close()

