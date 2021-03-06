from pythonmodules.ner import tester, NERFactory, corpora
from pycm.pycm_param import PARAMS_DESCRIPTION, PARAMS_LINK
from pycm.pycm_output import rounder as round_func
from functools import partial
from tabulate import tabulate as tabber
from argparse import ArgumentParser
import logging

logger = logging.getLogger(__name__)

if __name__ != '__main__':
    raise ImportError("this module cannot be imported")

txt_known_taggers = 'Currently available taggers: %s' % ', '.join(NERFactory.KNOWN_TAGGERS)

parser = ArgumentParser(description='Test NER taggers against GMB data')
parser.add_argument('amount', type=int, default=10, nargs='?',
                    help='Test the taggers with AMOUNT phrases, 0 for all (default 10)')
parser.add_argument('--tagger', action='append', default=[],
                    help='Include taggers to test, (if not set, includes all by default). %s' % txt_known_taggers)
parser.add_argument('--skip', action='append',
                    help='Skip certain taggers. %s' % txt_known_taggers)
parser.add_argument('--no-output', dest='no_output', default=False, action='store_true',
                    help='Don\'t output results')
parser.add_argument('--save-html', dest='save_html', action='store_true',
                    help='Save the results to html files')
parser.add_argument('--save-md', action='store_true',
                    help='Save results as MarkDown documents')
parser.add_argument('--log-level', type=str.upper, default='INFO', dest='log_level',
                    choices=logging._levelToName.values(),
                    help='Set the logging output level.')
parser.add_argument('--corpus', type=str, default='GMB',
                    help='The corpus to test against')
parser.add_argument('--precision', type=int, default=5,
                    help='The precision used for output of floating point numbers')
args = parser.parse_args()

loglevel = logging._nameToLevel[args.log_level]
logger.setLevel(loglevel)
logging.basicConfig(level=loglevel)

precision = args.precision
tabulate = partial(tabber, tablefmt='pipe', floatfmt='.%df' % precision, numalign="right")
rounder = partial(round_func, digit=precision)


def h(text, level=1, tablefmt='pipe'):
    return ('#' * level) + ' ' + text + "\n"


def stringify_result(tagger, result, links=None, tablefmt='simple'):
    output = h(tagger, 2, tablefmt)
    data = (
        ('Accuracy', 'Time', 'Total checked'),
        ('%.2f%%' % result.accuracy, '%dms' % result.time, result.total_checked)
    )
    output += tabulate(data, headers='firstrow', tablefmt=tablefmt)
    output += "\n\n"
    output += h('Confusion Matrix', 3, tablefmt)
    output += confusion_matrix_to_text(result.confusion_matrix, links=links, tablefmt=tablefmt)
    output += "\n"
    return output


def confusion_matrix_to_text(cm, links=None, tablefmt='simple'):
    classes = cm.classes
    table = cm.table
    class_stat = cm.class_stat
    overall_stat = cm.overall_stat

    headers = list(map(str, classes))
    headers.insert(0, 'Predict')
    classes.sort()
    data = [['Actual']]
    for key in classes:
        row = [table[key][i] for i in classes]
        # div = sum(row)
        # if div == 0:
        #     div = 1
        # row = list(map(lambda x: ('%.' + str(precision - 2) + 'f%%') % (x/div*100), row))
        row.insert(0, key)
        data.append(row)
    result = tabulate(data, headers=headers, tablefmt=tablefmt)
    result += "\n\n"

    result += h('Overall Statistics', 3, tablefmt)
    data = [(k.replace('_', ' '), rounder(v)) for k, v in overall_stat.items()]
    result += tabulate(data, headers=('Name', 'Value'), tablefmt=tablefmt)
    result += "\n\n"

    result += h('Class Statistics', 3, tablefmt)
    data = [['Class'] + list(map(str, classes)) + ['Description']]
    class_stat_keys = sorted(class_stat.keys())
    classes.sort()

    for key in class_stat_keys:
        row = list(map(rounder, [class_stat[key][i] for i in classes]))
        if links:
            row.append('[%s](%s)' % (PARAMS_DESCRIPTION[key].capitalize(), PARAMS_LINK[key]))
        else:
            row.append(PARAMS_DESCRIPTION[key].capitalize())
        row.insert(0, key)
        data.append(row)
    result += tabulate(data, headers='firstrow', tablefmt=tablefmt)
    return result


fmt = 'pipe'
if args.tagger:
    taggers = args.tagger
else:
    taggers = [tagger for tagger in NERFactory.KNOWN_TAGGERS]

if args.skip:
    taggers = [tagger for tagger in taggers if tagger not in args.skip]

corpus = args.corpus
corpus = getattr(corpora, corpus)

# print([a for a in corpus().read_entities()])
# exit()
results = tester.Tester(taggers, corpus=corpus()).test(args.amount)

if not args.no_output:
    print(h("Results", tablefmt='fancy_grid'))

for i, result in enumerate(results):
    tagger_name = taggers[i].replace(':', ' ')
    if not args.no_output:
        print(stringify_result(tagger_name, result, tablefmt='fancy_grid'))
    if args.save_md:
        with open('%s.md' % tagger_name, 'w') as f:
            f.write(stringify_result(tagger_name, result, links=True, tablefmt='pipe'))
    if args.save_html:
        result.confusion_matrix.save_html(tagger_name)

