# -*- coding: utf-8 -*-

from pythonmodules.mediahaven import MediaHaven

from pythonmodules.config import Config
from tqdm import tqdm
from pythonmodules.namenlijst import Conversions
from pythonmodules.profiling import timeit
from pysolr import Solr
from pythonmodules.multithreading import *
from pythonmodules.cache import DummyCacher

import logging
from functools import partial

logger = logging.getLogger(__name__)
config = Config()


class Importer:
    def __init__(self):
        self._solr = Solr(Config(section='solr')['url'])
        self._mh = MediaHaven(buffer_size=100)

    def add(self, item):
        self._solr.add([item])

    def process(self, item):
        if item is None:
            raise Exception("Invalid item passed (None)")

        if type(item) is not str:
            pid = item['externalId']
        else:
            pid = item
            item = self._mh.one('+(externalId:%s)' % pid)

        if not pid:
            raise "No pid for item %s" % (item,)

        language = ''
        try:
            language = item['mdProperties']['language'][0].lower()
        except Exception as e:
            logger.warning('no language found for %s', pid)
            logger.exception(e)

        alto = self._mh.get_alto(item)
        if not alto:
            logger.debug("no alto for pid '%s' " % (pid,))
            text = ''
        else:
            text = Conversions.normalize(alto.text)
        self.add(dict(id=pid, text=text, language=language))


class BulkImporter(Importer):
    def __init__(self, buffer_size=10):
        super().__init__()
        self._buffer = []
        self._buffer_size = buffer_size
        self.progress = None
        self.timeit = partial(timeit, min_time=1000, callback=self.onslow)

    def msg(self, message, *args):
        if self.progress is None:
            return
        if len(args):
            message = message % args
        self.progress.set_description(message)
        # self.progress.refresh()

    def onslow(self, ms, is_slow, txt, *args):
        if is_slow:
            # logger.warning('[SLOW %s:%dms]', txt, ms)
            self.msg('[SLOW %s:%dms]', txt, ms)
            logger.warning('Slow processing "%s" %dms' % (txt, ms))
        else:
            logger.info('Processed %s in %dms' % (txt, ms))

    def check_progress_buffer(self, force=False):
        l = len(self._buffer)
        if not force and l < self._buffer_size:
            self.msg('bufsize: %d', l)
            return
        buf, self._buffer = self._buffer, []
        logger.debug("Writing %d to solr", len(buf))
        self._solr.add(buf)
        self.msg('Written %d items to solr', len(buf))

    def add(self, item):
        self._buffer.append(item)
        self.check_progress_buffer()

    @multithreadedmethod(10, queue_buffer_size=200, pre_start=True, pass_thread_id=False)
    def process(self, item, *args, **kwargs):
        idx, new_item = item
        super().process(new_item, *args, **kwargs)

    def start(self, start_from=None, extra_search=''):
        if start_from is None:
            start_from = 0

        self.progress = tqdm(initial=start_from)
        with self.timeit('MH Search'):
            data = self._mh.search('+(workflow:GMS) +(archiveStatus:on_tape) %s' % extra_search, start_from)
            total = len(data)

        self.progress.total = total
        self.process._multithread.pbar = self.progress
        self.process(enumerate(data, 1 + start_from))
        self.check_progress_buffer(force=True)
        self.progress.close()


