# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from pywebserver.lib.solrimport import BulkImporter
import logging


parser = ArgumentParser(description='Bulk import ocr texts to solr')
parser.add_argument('--continue-from', help='Continue from row CONTINUE_FROM')
parser.add_argument('--debug', action='store_true', help='Show debug info')
parser.add_argument('--test', action='store_true', help='Run test')
args = parser.parse_args()

log_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s ' + logging.BASIC_FORMAT)
logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(log_level)

if args.continue_from:
    start = int(args.continue_from)
else:
    start = 0

if start:
    logger.info('Continuing from %d', start)

importer = BulkImporter(50)
importer.start(start)

