# -*- coding: utf-8 -*-

from pythonmodules.mediahaven import MediaHaven

from pythonmodules.config import Config
from tqdm import tqdm
from argparse import ArgumentParser
from pythonmodules.namenlijst import Conversions
from pythonmodules.profiling import timeit
from collections import deque
from binascii import crc32
from pysolr import Solr
from pythonmodules.multithreading import *

import logging
from functools import partial


def hasher(b):
    return crc32(b.encode('utf-8'))


use_bulk = False


parser = ArgumentParser(description='Import ocr texts to solr')
parser.add_argument('--clear', action='store_true', help='Clear the table before inserting')
parser.add_argument('--continue-from', help='Continue from row CONTINUE_FROM')
parser.add_argument('--debug', action='store_true', help='Show debug info')
parser.add_argument('--test', action='store_true', help='Run test')
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(log_level)

config = Config()

if args.continue_from:
    start = int(args.continue_from)
else:
    start = 0

if start:
    logger.info('Continuing from %d', start)


# if start == 0 and args.clear:
    # truncate collection first
    # todo

def onslow(ms, is_slow, txt, *args):
    global progress
    if is_slow:
        # logger.warning('[SLOW %s:%dms]', txt, ms)
        progress.set_description('[SLOW %s:%dms]' % (txt, ms))
        progress.refresh()
        logger.warning('Slow processing "%s" %dms' % (txt, ms))
    else:
        logger.info('Processed %s in %dms' % (txt, ms))
    pass


timeit = partial(timeit, min_time=1000, callback=onslow)

progress = tqdm()


class ImportWords:
    def __init__(self, buffer_size=10):
        self._buffer = deque([[], []])
        self._buffer_size = buffer_size
        self._solr = Solr(Config(section='wordsearcher')['solr'])
        self._mh = MediaHaven()

    def check_progress_buffer(self, force=False):
        if not force and len(self._buffer[0]) < self._buffer_size:
            return
        self._buffer.append([])
        self.write(self._buffer.popleft())

    # @multithreadedmethod(2)
    def write(self, buf, thread_id=None):
        logger.info("Writing %d to solr", len(buf))
        # print(buf)
        self._solr.add(buf)

    def add(self, item):
        logger.debug('append to queue (add to %d items) %s', len(self._buffer[0]), item)
        self._buffer[0].append(item)
        self.check_progress_buffer()

    @singlethreadedmethod(5, pbar=progress, pass_thread_id=False)
    def process(self, item):
        real_idx, item = item
        if item is None:
            raise Exception("args: %s" % str(real_idx))
        # logger.debug('process %d ' % real_idx)
        pid = item['externalId']
        if not pid:
            raise "No pid for item %s" % (item,)
        alto = self._mh.get_alto(pid)
        if not alto:
            logger.warning("no alto for #%d pid '%s' " % (real_idx, pid))
            text = ''
        else:
            text = Conversions.normalize(alto.text)
        self.add(dict(text=text, pid=pid))

    def start(self, start_from=None):
        if start_from is None:
            start_from = 0

        with timeit('MH Search'):
            if args.test:
                data = [{"test": True} for a in range(0, 10)]
            else:
                data = self._mh.search('+(workflow:GMS) +(archiveStatus:on_tape)', start)

            total = len(data) - start_from

        progress.total = total
        self.process(enumerate(data, 1 + start_from))
        self.check_progress_buffer(force=True)
        progress.close()


importer = ImportWords(50)
importer.start()

