# coding: utf-8

from pythonmodules.profiling import timeit
import logging
from lib.linker import Linker, Datasources, AttributeMapper
from tqdm import tqdm


def run(*args):
    logger = logging.getLogger('link_names')
    logger.setLevel(logging.INFO)
    log_file_handler = logging.FileHandler('link_names.log')
    logger.addHandler(log_file_handler)
    timeit.logger.addHandler(log_file_handler)
    logger.info('running with arguments: %s', args)

    if 'counts' in args:
        logger.info('will check counts only, will not attempt to do lookups!')

    if 'debug' in args:
        logging.basicConfig(level=logging.DEBUG)
        logger.info('debug mode')
        logger.setLevel(logging.DEBUG)

    if 'consecutive' in args:
        logger.info('will not run in parallel')

    if 'no-skips' in args:
        logger.info('will not skip frequent names')

    if 'only-skips' in args:
        logger.info('will only check frequent names')

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

    table = [a for a in args if a.split(':')[0] == 'table']
    if len(table):
        table = table[0].split(':', 2)[1]
    else:
        table = datasource['table'] if 'table' in datasource else None

    logger.info("Using datasource '%s'" % datasource)
    datasource = Datasources[datasource]

    extra_kwargs = {}
    if len(args) and args[0].isdigit():
        logger.warning('will skip %s', args[0])
        extra_kwargs['skip'] = int(args[0])

    linking = Linker(8 if 'consecutive' not in args else 1,
                     counts_only='counts' in args,
                     no_skips='no-skips' in args,
                     no_write='no-write' in args,
                     table=table,
                     only_skips='only-skips' in args)

    if linking.preset_list:
        def mapper(id):
            document['_id'] = id
            return datasource['func'](document=document, options=options, **extra_kwargs)

        l = len(linking.preset_list)
        people = datasource['func'](results=list(tqdm(map(mapper, linking.preset_list), total=l)))
        linking.length = l
        # document['_id'] = list(linking.preset_list)
        # people = datasource['func'](document=document, options=options, **extra_kwargs)
    else:
        people = datasource['func'](document=document, options=options, **extra_kwargs)

    if 'debug-sql' in args:
        logger.info('will show some sql debug info')
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    if 'clean' in args or not(any([a in args for a in ['debug-sql', 'debug', 'no-write', 'counts']])) and 'skip' not in extra_kwargs:
        msg = 'Clear table %s?' % linking.link._meta.db_table
        if input("%s (y/N) " % msg).strip().lower() == 'y':
            linking.clear()

    linking.start(people, extra_kwargs['skip'] if 'skip' in extra_kwargs else 0)
    logger.info(linking.counts)
