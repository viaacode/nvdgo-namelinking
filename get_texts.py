# -*- coding: utf-8 -*-

from pythonmodules.mediahaven import MediaHaven

from pythonmodules.config import Config
from tqdm import tqdm
from argparse import ArgumentParser
from pythonmodules.namenlijst import Conversions

from pythonmodules.profiling import timeit

from queue import Queue
from threading import Thread

from binascii import crc32

from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker
import logging
from functools import partial


def hasher(b):
    return crc32(b.encode('utf-8'))


use_bulk = False


parser = ArgumentParser(description='Import ocr texts to db table')
parser.add_argument('--clear', action='store_true', help='Clear the table before inserting')
parser.add_argument('--continue', action='store_true', help='Continue from last inserted row')
parser.add_argument('--continue-from', help='Continue from row CONTINUE_FROM')
parser.add_argument('--debug', action='store_true', help='Show debug info')
# parser.add_argument('--skip-words', action='store_true', help='Skip words inserts')
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(log_level)

if use_bulk:
    session = scoped_session(sessionmaker())

config = Config()
db = create_engine(config['db']['connection_url'])
db.connect()

if use_bulk:
    session.configure(bind=db)

meta = MetaData(db, reflect=True)

table_name = 'attestation_texts'
words_table_name = 'attestation_words'

table = meta.tables[table_name]
words_table = meta.tables[words_table_name]

if use_bulk:
    Base = automap_base(metadata=meta)
    Base.prepare()
    tables = dict(
        table=getattr(Base.classes, table_name),
        words_table=getattr(Base.classes, words_table_name)
    )

if args.continue_from:
    start = int(args.continue_from)
elif vars(args)['continue']:
    start = db.execute(func.max(table.c.id)).scalar()
else:
    start = 0

if start:
    logger.info('Continuing from %d', start)

mh = MediaHaven()
with timeit('MH Search'):
    data = mh.search('+(workflow:GMS) +(archiveStatus:on_tape)', start, 8)

if start == 0 and args.clear:
    # truncate table first
    logger.warning('gonna truncate %s and %s' % (table_name, words_table_name))
    with timeit('Truncating tables:'):
        logger.warning("Truncating %s and %s", table_name, words_table_name)
        db.execute('TRUNCATE TABLE %s, %s RESTART IDENTITY' % (table_name, words_table_name))

total = len(data) - start

progress = tqdm(total=total)


def onslow(ms, is_slow, txt, *args):
    global progress
    if is_slow:
        # logger.warning('[SLOW %s:%dms]', txt, ms)
        progress.set_description('[SLOW %s:%dms]' % (txt, ms))
        progress.refresh()
    pass


timeit = partial(timeit, min_time=1000, callback=onslow)


def process(real_idx, item, bulk=False):
    pid = item['externalId']
    if not pid:
        raise "No pid for item %s" % (item,)
    alto = mh.get_alto(pid)
    if not alto:
        logger.warning("no alto for #%d pid '%s' " % (real_idx, pid))
        text = ''
    else:
        text = Conversions.normalize(alto.text.lower())
    row = dict(id=real_idx, text=text, pid=pid)
    with timeit('_table insert (%d)' % len(text)):
        if bulk:
            session.bulk_insert_mappings(tables['table'], [row])
        else:
            db.execute(table.insert(), [row])

    # if len(text) and not args.skip_words:
    #     with timeit('calc hashes'):
    #         hashes = [dict(word_hash=h, texts_id=real_idx)
    #                   for h in set(map(hasher, (word for word in text.split(' ') if len(word))))]
    #
    #     if len(hashes):
    #         with timeit('words_table insert (%d)' % len(hashes)):
    #             if bulk:
    #                 session.bulk_insert_mappings(tables['words_table'], hashes)
    #             else:
    #                 db.execute(words_table.insert(), hashes)

    if bulk:
        session.commit()


q = Queue()


def worker():
    global q, progress
    while True:
        args = q.get()
        try:
            process(*args)
        except Exception as e:
            logger.exception(e)
        q.task_done()
        progress.update(1)


n_workers = 5
for i in range(n_workers):
    t = Thread(target=worker)
    t.daemon = True
    t.start()

for i, mh_item in enumerate(data):
    q.put([i + start + 1, mh_item, use_bulk])
q.join()
