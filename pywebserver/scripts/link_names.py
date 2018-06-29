# coding: utf-8

from pythonmodules.profiling import timeit
import logging
from lib.linker import Linker, Datasources, AttributeMapper
from lib.helpers import GeneratorLimit


def run(*args):
    logger = logging.getLogger('link_names')
    logger.setLevel(logging.INFO)
    log_file_handler = logging.FileHandler('link_names.log')
    logger.addHandler(log_file_handler)
    timeit.logger.addHandler(log_file_handler)
    logger.info('running with arguments: %s' % (' "%s"' * len(args)), *args)

    if 'counts' in args:
        logger.info('will check counts only, will not attempt to do lookups!')

    if 'debug' in args:
        logger.info('debug mode')
        logger.setLevel(logging.DEBUG)

    if 'consecutive' in args:
        logger.info('will not run in parallel')

    if 'no-skips' in args:
        logger.info('will not skip frequent names')

    if 'no-write' in args:
        logger.info('don\'t write results to db')

    document = {
        # '_id': '4a7795fd-6fa0-4dc3-bcc3-4ee82c371077'
        # "died_year": 1914
    }

    ids = [a for a in args if a[0:3] == 'id:']
    if len(ids):
        document['_id'] = ids[0][3:]
        logger.info('will only check %s' % document['_id'])

    options = [
        # 'EXTEND_DIED_PLACE',
        # 'EXTEND_DIED_DATE'
    ]

    datasource = [k for k, v in Datasources.items() if k in args]
    if len(datasource):
        datasource = datasource[0]
    else:
        datasource = 'namenlijst'

    logger.info("Using datasource '%s'" % datasource)
    datasource = Datasources[datasource]
    people = datasource['func'](document=document, options=options)

    if len(args) and args[0].isdigit():
        logger.info('will only do first %s' % args[0])
        if len(people) > int(args[0]):
            people = GeneratorLimit(people, int(args[0]))

    linking = Linker(5 if 'consecutive' not in args else 1,
                     counts_only='counts' in args,
                     no_skips='no-skips' in args,
                     no_write='no-write' in args,
                     table=datasource['table'] if 'table' in datasource else None)

    if 'debug-sql' in args:
        logger.info('will show some sql debug info')
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    linking.start(people)
    logger.info(linking.counts)
