from pythonmodules.ner import tester, NERFactory
from argparse import ArgumentParser
import json


if __name__ != '__main__':
    raise ImportError("this module cannot be imported")

parser = ArgumentParser(description='Test NER taggers against GMB data')
parser.add_argument('--skip', action='append',
                    help='Skip certain taggers, currently available taggers: %s' % ', '.join(NERFactory.KNOWN_TAGGERS))
parser.add_argument('amount', type=int, default=10, nargs='?',
                    help='Test the taggers with AMOUNT phrases, 0 for all (default 10)')
parser.add_argument('corpus', type=str, default='GMB',
                    help='The corpus to test against (TODO)')
args = parser.parse_args()

taggers = [tagger for tagger in NERFactory.KNOWN_TAGGERS if tagger not in args.skip]
t = tester.Tester(taggers)

# show the namedtuples as dicts instead of arrays for better readability
results = [f._asdict() for f in t.test(args.amount)]
print(json.dumps(dict(zip(taggers, results)), indent=4))
