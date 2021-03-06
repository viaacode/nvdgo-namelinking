# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser
from pythonmodules.multithreading import multithreaded
from pywebserver.lib.matcher import Meta
import logging
import csv
import sys
import json
from pythonmodules.alto import Extent

parser = ArgumentParser(description='Generates the export csv')
parser.add_argument('--start', type=int, nargs='?', help='start from')
parser.add_argument('--table', help='Origin table', default='attestation_linksolr')
parser.add_argument('--limit', type=int, help='limit amount done')
parser.add_argument('--clear-log-file', default=False, action='store_true', help='Empty the log file first')
parser.add_argument('--log-file', type=str, default='generate_csv.log', help='Set log file name')
parser.add_argument('--csv', type=str, help='The csv to write te results to, if not given will output to stdout')
parser.add_argument('--where', type=str, default=None, help='Extra conditions')
parser.add_argument('--debug', default=False, action='store_true')
parser.add_argument('--recalculate-textblock', default=False, action='store_true')
parser.add_argument('--recalculate-meta', default=False, action='store_true')

args = parser.parse_args()

if args.clear_log_file:
    open(args.log_file, 'w').close()

logging.basicConfig()
logger = logging.getLogger()
fh = logging.FileHandler(args.log_file)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

if args.debug:
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

csv_file = sys.stdout if args.csv is None else open(args.csv, 'w')


where = ''
if args.where:
    where = 'AND %s ' % (args.where,)

config = Config(section='db')
conn = psycopg2.connect(config['connection_url'])
cur = conn.cursor()

with timeit('SELECT', 5000):
    q = "SELECT id, pid, nmlid, entity, score, meta " \
        "FROM %s " \
        "WHERE status != 2 AND status != 4 AND score > 0 %s " \
        "ORDER BY pid ASC " % (args.table, where)
    if args.limit:
        q += ' LIMIT %d' % int(args.limit)
    if args.start:
        q += ' OFFSET %d' % int(args.start)
    cur.execute(q)

headers = ('pid', 'page', 'type', 'external_id', 'name', 'lod', 'meta')
writer = csv.writer(csv_file)
writer.writerow(headers)

i = 0


get_meta = Meta(force_regen=args.recalculate_meta)


@multithreaded(10, pre_start=True, pass_thread_id=False)
def process(row):
    global i, conn
    try:
        id_, full_pid, external_id, entity, score, meta = row
        meta = json.loads(meta)
        orig_meta = meta
        meta = get_meta(full_pid, external_id, entity, score, meta)

        pid, pid_date, page = full_pid.split('_', 2)
        page = int(page)

        full_name = meta['name']

        if orig_meta != meta:
            cur_write = conn.cursor()
            cur_write.execute('UPDATE %s SET meta = %%s WHERE id=%%s' % args.table,
                              (json.dumps(meta), id_))
            cur_write.close()

        lod = {
            "af:confidence": score,
            "@graph": [
                {
                    "@id": "https://hetarchief.be/pid/%s/%d" % (pid, page),
                    "mentions": [
                        {
                            "@id": "https://database.namenlijst.be/publicsearch/#/person/_id=%s" % (external_id,),
                            "@type": "Person",
                            "name": full_name,
                            "label": full_name,
                            "topicOf": {
                                "@id": "https://database.namenlijst.be/publicsearch/#/person/_id=%s" % (external_id,),
                                "partOf": "https://database.namenlijst.be"
                            }
                        }
                    ]
                }
            ]
        }

        lod = json.dumps(lod)
        if args.recalculate_textblock:
            extents = map(Extent.from_coords, meta['highlight'])
            meta['zoom'] = Extent.extend(*extents).pad(-200).as_coords()

        meta = json.dumps(meta)
        csv_row = [pid, page, 'namenlijst', external_id, entity, lod, meta]
        writer.writerow(csv_row)
        i += 1
        if i == 100:
            conn.commit()
            i = 0
            csv_file.flush()

    except Exception as e:
        logger.warning('exception for %s', 'namenlijst/%s/%s/%s' % (full_pid, external_id, entity.replace(' ', '/')))
        logger.exception(e)


process._multithread.pbar = tqdm(total=cur.rowcount)
process(cur)

csv_file.flush()

if csv_file is not sys.stdout:
    csv_file.close()

cur.close()
conn.commit()
conn.close()

