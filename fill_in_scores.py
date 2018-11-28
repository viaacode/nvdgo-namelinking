# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser
from pywebserver.lib.matcher import Rater, Meta
import logging
from pythonmodules.multithreading import multithreaded
import json

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
    q = 'SELECT id, pid, nmlid, entity, score, meta FROM %s %s ORDER BY status DESC, score DESC, pid ASC' % (args.table, where_clause)
    if args.limit:
        q += ' LIMIT %d' % int(args.limit)
    if args.start:
        q += ' OFFSET %d' % int(args.start)
    cur.execute(q)

get_meta = Meta()


@multithreaded(10, pre_start=True, pass_thread_id=False)
def process(row):
    try:
        id_, full_pid, external_id, entity, score, meta = row
        rater = Rater(full_pid, external_id, entity)
        cur_rating = score
        meta_old = None
        if meta:
            meta_old = json.loads(meta)

        meta = get_meta(full_pid, external_id, entity, score, meta)
        new_rating = 0
        try:
            rating = rater.ratings()
            meta['rating_breakdown'] = {k: rating.scores[k].rating for k in rating.scores}
            new_rating = rating.total
        except KeyError as e:
            logger.warning(e)

        if cur_rating == new_rating and meta == meta_old:
            return
        cur2 = conn2.cursor()
        cur2.execute('UPDATE ' + args.table + ' SET score = %s, meta = %s WHERE id=%s', [new_rating, json.dumps(meta), id_])
        cur2.close()
        conn2.commit()
    except Exception as e:
        url = 'http://do-tst-mke-01.do.viaa.be/attestation/info/model-namenlijst/%s/%s/%s' % \
              (full_pid, external_id, entity.replace(' ', '/'))
        logger.warning('exception for %s', url)
        logger.exception(e)


process._multithread.pbar = tqdm(total=cur.rowcount)
process(cur)

conn.commit()
try:
    conn2.commit()
except Exception as e:
    logger.info(e)

cur.close()
conn.close()
conn2.close()

