from pythonmodules.config import Config
from pythonmodules.mediahaven import MediaHaven
from pythonmodules.namenlijst import Namenlijst
from pysolr import Solr
from sickle.oaiexceptions import IdDoesNotExist
from argparse import ArgumentParser
import psycopg2
import logging


class Services:
    def __init__(self):
        self._config = Config()

    def solr(self):
        solr_ = Solr(self._config['solr']['url'], timeout=5)
        solr_.search('*:*', rows=1)

    def mediahaven(self):
        mh = MediaHaven(self._config)
        mh.one('+(externalId:f76639mh4g_19180801_0001)')

    def namenlijst(self):
        nl = Namenlijst(self._config)
        nl.findPerson(document={'_id': '91f8e0eb-05c4-49ad-9730-99168b39263d'})

    def oai(self):
        mh = MediaHaven(self._config)
        fragment_id = 'EeZNC2b9TeYMKMQRNcVJnumk'
        try:
            mh.oai().GetRecord(identifier='umid:%s' % fragment_id, metadataPrefix='mets')
        except IdDoesNotExist:
            pass

    def db(self):
        conn = psycopg2.connect(self._config['db']['connection_url'])
        cur = conn.cursor()
        cur.close()
        conn.close()


possible_services = [name for name in dir(Services) if name[0] != '_']
possible_services.insert(0, 'all')

parser = ArgumentParser('Test connections to various services')
parser.add_argument('services', default='all', nargs='*', choices=possible_services,
                    help='Which services to test connections to')
parser.add_argument('--hide-exceptions', action='store_true', default=False,
                    help="Don't output the exceptions")
parser.add_argument('--silent', action='store_true', default=False,
                    help="Don't output anything, just return exit code")
parser.add_argument('--verbose', action='store_true', default=False,
                    help='Be verbose, output all debug logs')
parser.add_argument('--no-color', action='store_true', default=False,
                    help="Do not use ANSI color codes in output")

arg = parser.parse_args()

if arg.verbose:
    logging.basicConfig(level=logging.DEBUG)

services = arg.services
if 'all' in services:
    services = possible_services
    services.remove('all')

serv = Services()
failed = False
for service_name in services:
    try:
        if not arg.silent:
            print('Check %s: ' % service_name, end='', flush=True)
        getattr(serv, service_name)()
        if not arg.silent:
            print('[OK]' if arg.no_color else '\x1B[38;32m[OK]\x1B[0m', flush=True)
    except Exception as e:
        failed = True
        if not arg.silent:
            print('[ERR]' if arg.no_color else '\x1B[48;41m[ERR]\x1B[0m', flush=True)
        if not arg.hide_exceptions and not arg.silent:
            print('%s: %s' % (type(e), str(e)), flush=True)

exit(1 if failed else 0)
