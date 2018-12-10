# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser
from pywebserver.lib.matcher import Rater, Meta
import logging
from pythonmodules.multithreading import multithreaded, singlethreaded
from pythonmodules.mediahaven import MediaHaven
from pythonmodules.namenlijst import Namenlijst
import json
import re

parser = ArgumentParser(description='Add/fill in scores in link tables')
parser.add_argument('--start', type=int, nargs='?', help='start from')
parser.add_argument('--table', help='Origin table', default='attestation_linksolr')
parser.add_argument('--limit', type=int, help='limit amount done')
parser.add_argument('--clear-log-file', default=False, action='store_true', help='Empty the log file first')
parser.add_argument('--log-file', type=str, default='fill_in_scores.log', help='Set log file name')
parser.add_argument('--where', type=str, help='Extra where clause to pass to the select query (eg. "status=1")')
parser.add_argument('--debug', action='store_true', default=False, help='Show debug logging')
args = parser.parse_args()

if args.clear_log_file:
    open(args.log_file, 'w').close()

logLevel = logging.DEBUG if args.debug else logging.WARNING
logLevel = logging.WARNING
logging.basicConfig(level=logLevel)
logger = logging.getLogger()
logger.setLevel(logLevel)
fh = logging.FileHandler(args.log_file)
logger.addHandler(fh)

table = args.table
wheres = args.where

config = Config(section='db')
conn = psycopg2.connect(config['connection_url'])
conn2 = psycopg2.connect(config['connection_url'])
cur = conn.cursor()

with timeit('SELECT', 5000):
    where_clause = ('WHERE %s' % wheres) if wheres else ''
    order_by = 'status DESC, pid ASC, id DESC'
    order_by = 'nmlid DESC'
    order_by = 'pid ASC'
    q = 'SELECT DISTINCT(pid) FROM %s %s'
    q += ' GROUP BY pid'
    q += ' ORDER BY %s' % (order_by,)
    q = q % (table, where_clause)
    if args.limit:
        q += ' LIMIT %d' % int(args.limit)
    if args.start:
        q += ' OFFSET %d' % int(args.start)
    cur.execute(q)

get_meta = Meta()

remove_double_spaces = re.compile('\\s+')
model_name = args.table.split('_')[-1]

query = 'SELECT id, pid, nmlid, entity, score, meta FROM %s WHERE %s AND pid = %%s ORDER BY id ASC' % \
        (table, wheres if wheres else '1')


@multithreaded(10, pre_start=True, pass_thread_id=False, pbar=tqdm(total=cur.rowcount))
def process(row):
    pid = row[0]

    with conn2.cursor() as cur3:
        cur3.execute(query, (pid,))
        for row in cur3:
            try:
                process_pid(row)
            except Exception as e:
                logger.error(e)


def process_pid(row):
    try:
        id_, full_pid, external_id, entity, score, meta = row
        entity = remove_double_spaces.sub(' ', entity)
        with timeit('Rater init', 1e3):
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
            meta['rating_multiplier'] = rating.total_multiplier
            new_rating = rating.total
        except KeyError as e:
            logger.warning(e)

        if cur_rating == new_rating and meta == meta_old:
            return

        with timeit('SLOW UPDATE %s' % id_, 1e3), conn2.cursor() as cur2:
            cur2.execute('UPDATE ' + args.table + ' SET score = %s, meta = %s WHERE id=%s',
                         [new_rating, json.dumps(meta), id_])
            conn2.commit()
    except Exception as e:
        try:
            url = 'http://do-tst-mke-01.do.viaa.be/attestation/info/model-%s/%s/%s/%s' % \
                  (model_name, full_pid, external_id, entity.replace(' ', '/'))
        except Exception as e2:
            url = str(e2)
        logger.warning('exception for %s', url)
        logger.exception(e)


process(cur)

conn.commit()
try:
    conn2.commit()
except Exception as e:
    logger.info(e)

cur.close()
conn.close()
conn2.close()
