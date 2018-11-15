# coding: utf-8

from pythonmodules.config import Config
import psycopg2
from tqdm import tqdm
from pythonmodules.profiling import timeit
from argparse import ArgumentParser
from pythonmodules.namenlijst import Namenlijst
from pythonmodules.mediahaven import MediaHaven
from pythonmodules.multithreading import multithreaded
import logging
import csv
import sys
import json


parser = ArgumentParser(description='Generates the export csv')
parser.add_argument('--start', type=int, nargs='?', help='start from')
parser.add_argument('--table', help='Origin table', default='attestation_linksolr2')
parser.add_argument('--limit', type=int, help='limit amount done')
parser.add_argument('--clear-log-file', default=False, action='store_true', help='Empty the log file first')
parser.add_argument('--log-file', type=str, default='generate_csv.log', help='Set log file name')
parser.add_argument('--csv', type=str, help='The csv to write te results to, if not given will output to stdout')
parser.add_argument('--where', type=str, default=None, help='Extra conditions')
parser.add_argument('--debug', default=False, action='store_true')

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
    q = "SELECT id, pid, nmlid, entity, score, status, meta " \
        "FROM %s " \
        "WHERE status != 2 %s " \
        "ORDER BY pid ASC " % (args.table, where)
    if args.limit:
        q += ' LIMIT %d' % int(args.limit)
    if args.start:
        q += ' OFFSET %d' % int(args.start)
    cur.execute(q)

headers = ('pid', 'page', 'type', 'external_id', 'name', 'lod', 'meta')
writer = csv.writer(csv_file)
writer.writerow(headers)
nl = Namenlijst()
mh = MediaHaven()

i = 0


@multithreaded(10, pre_start=True, pass_thread_id=False)
def process(row):
    global i, conn, cur_write
    try:
        id, full_pid, external_id, entity, score, status, meta = row
        attestation_id = 'namenlijst/%s/%s/%s' % (full_pid, external_id, entity.replace(' ', '/'))
        pid, pid_date, page = full_pid.split('_', 2)
        page = int(page)
        if score > 0.99:
            score = 0.99
        if meta is not None:
            meta = json.loads(meta)
            full_name = meta['name']
        else:
            logger.info('Generate meta data for %s', attestation_id)
            person = nl.get_person_full(external_id)
            full_name = person.names.name
            extra = dict()
            extra['country'] = person.born_place['country_code'].upper()
            extra['died_age'] = person.died_age

            subtitle = []

            if person.born_date is not None:
                if len(person.born_place['name']):
                    subtitle.append('\u00B0 %d %s' % (person.born_date.year, person.born_place['name']))
                else:
                    subtitle.append('\u00B0 %d' % (person.born_date.year,))

            if person.died_date is not None:
                if len(person.died_place['name']):
                    subtitle.append('\u2020 %d %s' % (person.died_date.year, person.died_place['name']))
                else:
                    subtitle.append('\u2020 %d' % (person.died_date.year,))

            subtitle = ', '.join(subtitle)

            alto = mh.get_alto(full_pid)
            search_res = alto.search_words([entity.split(' ')])
            extent_textblock = search_res['extent_textblocks']
            extents_highlight = [word['extent'] for word in search_res['words']]

            if search_res['correction_factor'] != 1:
                for word in extents_highlight:
                    word.scale(search_res['correction_factor'], inplace=True)
                extent_textblock.scale(search_res['correction_factor'], inplace=True)

            extent_textblock = extent_textblock.as_coords()
            extents_highlight = [extent.as_coords() for extent in extents_highlight]

            meta = {
                "name": full_name,
                "found_name": entity,
                "subtitle": subtitle,
                "quality": score,
                "zoom": extent_textblock,
                "highlight": extents_highlight,
                "full_pid": full_pid,
                "attestation_id": attestation_id,
                "coords_correctionfactor": search_res['correction_factor'],
                "extra": extra
            }

            meta = json.dumps(meta)

            cur_write = conn.cursor()
            cur_write.execute('UPDATE %s SET meta = %%s WHERE id=%%s' % args.table,
                              (meta, id))
            cur_write.close()

        lod = {
            "http://purl.org/ontology/af/confidence": score,
            "@graph": [
                {
                    "@id": "https://hetarchief.be/pid/%s/%d" % (pid, page),
                    "http://schema.org/mentions": [
                        {
                            "@id": "http://culturize.ilabt.imec.be/soldiers/data/%s" % (external_id,),
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


# for row in tqdm(cur, total=cur.rowcount):
#     run(*row)

process._multithread.pbar = tqdm(total=cur.rowcount)
process(cur)


if csv_file is not sys.stdout:
    csv_file.close()

cur_write.close()
cur.close()
conn.close()

