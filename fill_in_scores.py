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
from math import isclose
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
parser.add_argument('--threads', type=int, default=10, help='Amount of threads')
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
wheres = args.where + ' AND ' if args.where else ''
wheres += 'status != 4 '  # skip skips

config = Config(section='db')
conn = psycopg2.connect(config['connection_url'])
cur = conn.cursor()

with timeit('SELECT', 5000):
    q = '''
        SELECT 
            pid, 
            COUNT(*) as row_count 
        FROM %s 
        WHERE %s 
        GROUP BY pid 
        ORDER BY row_count DESC
'''

    q = q % (table, wheres)
    if args.limit:
        q += ' LIMIT %d' % int(args.limit)
    if args.start:
        q += ' OFFSET %d' % int(args.start)
    cur.execute(q)

get_meta = Meta()

remove_double_spaces = re.compile('\\s+')
remove_quality = re.compile(r' "quality": [0-9]\.[0-9]+,')
remove_ratingmultipl = re.compile(r', "rating_multiplier": [0-9]\.[0-9]+')
model_name = args.table.split('_')[-1]

query = 'SELECT id, pid, nmlid, entity, score, meta FROM %s WHERE %s AND pid = %%s ORDER BY id ASC' % \
        (table, wheres)


@multithreaded(args.threads, pre_start=True, pass_thread_id=False, pbar=tqdm(total=cur.rowcount))
def process(row):
    pid = row[0]

    with conn.cursor() as cur3:
        cur3.execute(query, (pid,))
        if not cur3.rowcount:
            return

        r = 0
        for row in cur3:  # tqdm(cur3, total=cur3.rowcount, desc=pid):
            try:
                process_pid(row)
                r += 1
            except Exception as e:
                logger.error(e)
            if r >= 10:
                r = 0
                conn.commit()
        conn.commit()


def meta_to_comp_meta(meta):
    if meta is not None:
        meta = remove_quality.sub('', meta)
        meta = remove_ratingmultipl.sub('', meta)
    return meta


def process_pid(row):
    try:
        id_, full_pid, external_id, entity, score, meta = row
        entity = remove_double_spaces.sub(' ', entity)
        with timeit('Rater init', 1e3):
            rater = Rater(full_pid, external_id, entity)
        cur_rating = score
        meta_old = None
        if meta:
            meta_old = meta

        try:
            meta = get_meta(full_pid, external_id, entity, score, meta)
        except KeyError as e:
            logger.warning(e)
            with conn.cursor() as cur2:
                cur2.execute('UPDATE ' + args.table + ' SET status=4 WHERE id=%s', [id_])
                # conn.commit()

        new_score = 0
        try:
            rating = rater.ratings()
            meta['rating_breakdown'] = {k: rating.scores[k].rating for k in rating.scores}
            meta['rating_multiplier'] = rating.total_multiplier
            new_score = rating.total
        except KeyError as e:
            logger.warning(e)

        toset = dict()
        if not isclose(cur_rating, new_score, abs_tol=.0001):
            toset['score'] = new_score

        if 'quality' in meta:
            del meta['quality']
        meta = json.dumps(meta)

        if meta_to_comp_meta(meta) != meta_to_comp_meta(meta_old):
            toset['meta'] = meta

        if not len(toset):
            return

        with timeit('SLOW UPDATE %s' % id_, 1e3), conn.cursor() as cur2:
            keys = ','.join([k + ' = %s' for k in toset.keys()])
            values = [toset[k] for k in toset.keys()]
            values.append(id_)
            cur2.execute('UPDATE ' + args.table + ' SET ' + keys + ' WHERE id=%s', values)
            # conn2.commit()
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
# try:
#     conn2.commit()
# except Exception as e:
#     logger.info(e)

cur.close()
conn.close()
# conn2.close()
