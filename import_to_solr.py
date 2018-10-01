# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from pywebserver.lib.solrimport import BulkImporter
import logging
from pysolr import Solr
from pythonmodules.config import Config


parser = ArgumentParser(description='Bulk import ocr texts to solr')
parser.add_argument('--continue-from', help='Continue from row CONTINUE_FROM')
parser.add_argument('--debug', action='store_true', help='Show debug info')
parser.add_argument('--continue', action='store_true', dest='continue_', help='Continue (based on count in solr)')
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s ' + logging.BASIC_FORMAT)
logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(log_level)

if args.continue_from:
    start = int(args.continue_from)
elif args.continue_:
    solr = Solr(Config(section='solr')['url'])
    res = solr.search(q='*:*', rows=1)
    start = res.hits
else:
    start = 0

if start:
    logger.info('Continuing from %d', start)

importer = BulkImporter(50)
importer.start(start)

