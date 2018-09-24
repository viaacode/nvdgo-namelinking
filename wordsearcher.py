from argparse import ArgumentParser
from pythonmodules.wordsearcher import *
import logging
import inspect


class Commands:
    def get_args(self, *args):
        parser = ArgumentParser(description='Some actions to do with wordsearcher')
        subparsers = parser.add_subparsers(title='command')
        subparsers.required = True
        subparsers.dest = 'command'

        parsers = [a for a, b in inspect.getmembers(type(self)) if a[0] != '_']
        parsers = {k: subparsers.add_parser(k) for k in parsers}

        prof = parsers['profiling']
        prof.add_argument('--threads', default=list(range(1, 11)), nargs='+',
                          help='The amount of threads used for the profiling (default: %(default)s)')
        prof.add_argument('--output', default=False, action='store_true',
                          help='Output profiling data straight to screen')
        prof.add_argument('--output-file', default='profiling.csv',
                          help='The file to store the profiling data to')
        prof.add_argument('--no-file', default=False, action='store_true',
                          help='Do not write the profiling output to file')

        imps = parsers['importsolr']
        imps.add_argument('--offset', default=None, type=int, 
                          help='Continue from offset (default: %(default)s)')

        for p in parsers.values():
            p.add_argument('--path', help='The path to the indexes directory (default: %(default)s)',
                           default='./indexes')
            p.add_argument('--verbosity', type=str.upper, default='INFO',
                           choices=logging._levelToName.values(),
                           help='Set the logging output level.')

        return parser.parse_args(*args)

    def __init__(self):
        args = self.get_args()
        loglevel = logging._nameToLevel[args.verbosity]
        logging.basicConfig(level=loglevel)

        self.args = args
        self.searcher = WordSearcherAdmin(args.path)
        getattr(self, args.command)()

    def profiling(self):
        cb = ProfilingResultAggregatorCallback()
        if self.args.output:
            cb.append(ProfilingResultPrintCallback())

        if not self.args.no_file:
            cb.append(ProfilingResultCsvCallback(file=self.args.output_file))

        if not len(cb):
            self.logger.warning('Profiling results are being ignored (no callbacks)')

        self.searcher.do_profiling(threads=self.args.threads, callback=cb)

    def importsolr(self):
        self.searcher.import_solr()


Commands()
