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
parser.add_argument('--where', type=str, help='Extra where clause to pass to the select query (eg. "status=1")')
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
    where_clause = ('WHERE %s' % args.where) if args.where else ''
    q = 'SELECT pid, nmlid, entity, id, score FROM %s %s ORDER BY status DESC, score DESC, pid ASC' % (args.table, where_clause)
    if args.limit:
        q += ' LIMIT %d' % int(args.limit)
    if args.start:
        q += ' OFFSET %d' % int(args.start)
    cur.execute(q)


@multithreaded(10, pre_start=True, pass_thread_id=False)
def process(row):
    try:
        rater = Rater(row[0], row[1], row[2])
        identifier = row[3]
        cur_rating = row[4]
        rating = rater.ratings()
        if cur_rating == rating.total:
            return
        cur2 = conn2.cursor()
        cur2.execute('UPDATE ' + args.table + ' SET score = %s WHERE id=%s', [rating.total, identifier])
        cur2.close()
        conn2.commit()
    except Exception as e:
        url = 'http://do-tst-mke-01.do.viaa.be/attestation/info/model-namenlijst/%s/%s/%s' % (row[0], row[1], row[2].replace(' ', '/'))
        logger.warning('exception for %s ( %s )', row, url)
        logger.exception(e)


process._multithread.pbar = tqdm(total=cur.rowcount)
process(cur)

conn.commit()
cur.close()
conn.close()
conn2.close()
