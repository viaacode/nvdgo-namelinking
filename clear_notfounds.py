# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser
from pywebserver.lib.matcher import Rater, Matcher
import logging
from pythonmodules.multithreading import multithreaded
from pysolr import Solr


parser = ArgumentParser(description='Add/fill in scores in link tables')
parser.add_argument('--start', type=int, nargs='?', help='start from')
parser.add_argument('--table', help='Origin table', default='attestation_linksolr2')
parser.add_argument('--limit', type=int, help='limit amount done')
parser.add_argument('--log-file', type=str, default='clears.log', help='Set log file name')
parser.add_argument('--where', type=str, help='Extra where clause to pass to the select query (eg. "status=1")')
args = parser.parse_args()

logging.basicConfig()
logger = logging.getLogger()
fh = logging.FileHandler(args.log_file)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

_solr = Solr(Config(section='solr')['url'])

config = Config(section='db')
conn = psycopg2.connect(config['connection_url'])
conn2 = psycopg2.connect(config['connection_url'])
cur = conn.cursor()
with timeit('SELECT', 5000):
    where_clause = ('WHERE %s' % args.where) if args.where else ''
    q = 'SELECT pid, nmlid, entity, id, score FROM %s %s ORDER BY pid ASC' % (args.table, where_clause)
    if args.limit:
        q += ' LIMIT %d' % int(args.limit)
    if args.start:
        q += ' OFFSET %d' % int(args.start)
    cur.execute(q)


@multithreaded(10, pre_start=True, pass_thread_id=False)
def process(row):
    try:
        res = _solr.search('id:%s' % row[0], rows=1, fl=['text', 'language'])

        if res.hits == 0:
            logger.warning('pid %s not found', row[0])
            return

        identifier = row[3]
        matcher = Matcher(res.docs[0]['text'], row[2])
        cur_rating = row[4]
    except IndexError as e:
        logger.warning(str(e))
        if 'Could not find base text' in str(e):
            logger.warning('REMOVING %s', row)
            cur2 = conn2.cursor()
            cur2.execute('DELETE FROM ' + args.table + ' WHERE id=%s', [identifier])
            cur2.close()
            conn2.commit()
        else:
            raise e
    except Exception as e:
        url = 'http://do-tst-mke-01.do.viaa.be/attestation/info/model-namenlijst/%s/%s/%s' % \
              (row[0], row[1], row[2].replace(' ', '/'))
        logger.warning('exception for %s ( %s )', row, url)
        logger.exception(e)


process._multithread.pbar = tqdm(total=cur.rowcount)
process(cur)

conn.commit()
cur.close()
conn.close()
conn2.close()

