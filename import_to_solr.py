# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from pywebserver.lib.solrimport import BulkImporter
import logging
from pysolr import Solr
from pythonmodules.config import Config
import sys

parser = ArgumentParser(description='Bulk import ocr texts to solr')
parser.add_argument('--continue-from', help='Continue from row CONTINUE_FROM')
parser.add_argument('--debug', action='store_true', help='Show debug info')
parser.add_argument('--continue', action='store_true', dest='continue_', help='Continue (based on count in solr)')
parser.add_argument('--log-file', default=False, help='Write logs to a file')
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.WARNING

logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(log_level)

ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s ' + logging.BASIC_FORMAT)
ch.setLevel(log_level)
ch.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(ch)

if args.log_file:
    logger.info('Will write logs to %s', args.log_file)
    fh = logging.FileHandler(args.log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)
    root_logger.setLevel(logging.INFO)

if args.continue_from:
    start = int(args.continue_from)
elif args.continue_:
    solr = Solr(Config(section='solr')['url'])
    res = solr.search(q='*:*', rows=1)
    start = max(res.hits - 1000, 0)
else:
    start = 0

if start:
    logger.info('Continuing from %d', start)

importer = BulkImporter(50)
importer.start(start)

