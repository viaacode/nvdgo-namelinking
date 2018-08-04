from pythonmodules.ner import tester, NERFactory
from argparse import ArgumentParser
from pycm.pycm_param import PARAMS_DESCRIPTION, PARAMS_LINK
from functools import partial
from tabulate import tabulate as tabber


if __name__ != '__main__':
    raise ImportError("this module cannot be imported")

precision = 5
tabulate = partial(tabber, tablefmt='pipe', floatfmt='.%df' % precision, numalign="right")


def rounder(input_number, digit=5, to_str=False):
    if input_number is None:
        input_number = 0

    if isinstance(input_number, tuple):
        rmap = partial(rounder, to_str=True, digit=digit)
        return '(%s)' % ', '.join(map(rmap, input_number))

    if not to_str:
        if isinstance(input_number, int):
            return input_number

        try:
            return float(input_number)
        except Exception:
            return input_number

    if isinstance(input_number, int):
        return '%d' % input_number

    return ('%.' + str(digit) + 'f') % round(input_number, digit)


def confusion_matrix_to_text(cm):
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
        row.insert(0, key)
        data.append(row)
    result = tabulate(data, headers=headers)

    result += "\n\n### Overall Statistics " + "\n\n"
    data = [(k, rounder(v)) for k, v in overall_stat.items()]
    result += tabulate(data, headers=('Name', 'Value'))

    result += "\n\n### Class Statistics\n\n"
    data = [['Classes'] + list(map(str, classes))]
    class_stat_keys = sorted(class_stat.keys())
    classes.sort()

    for key in class_stat_keys:
        row = list(map(rounder, [class_stat[key][i] for i in classes]))
        row.insert(0, '%s (%s)' % (PARAMS_DESCRIPTION[key].capitalize(), key))
        data.append(row)
    result += tabulate(data, headers='firstrow')
    return result


parser = ArgumentParser(description='Test NER taggers against GMB data')
parser.add_argument('--skip', action='append',
                    help='Skip certain taggers, currently available taggers: %s' % ', '.join(NERFactory.KNOWN_TAGGERS))
parser.add_argument('amount', type=int, default=10, nargs='?',
                    help='Test the taggers with AMOUNT phrases, 0 for all (default 10)')
parser.add_argument('corpus', type=str, default='GMB',
                    help='The corpus to test against (TODO)')
args = parser.parse_args()


fmt = 'pipe'
taggers = [tagger for tagger in NERFactory.KNOWN_TAGGERS if tagger not in args.skip]
t = tester.Tester(taggers)

# show the namedtuples as dicts instead of arrays for better readability
results = [f._asdict() for f in t.test(args.amount)]

output = '# Results'
for i, result in enumerate(results):
    output += "\n\n## %s\n\n" % taggers[i]
    data = (
        ('Accuracy', 'Time', 'Total checked'),
        ('%.2f%%' % result['accuracy'], '%dms' % result['time'], result['total_checked'])
    )
    output += tabulate(data, headers='firstrow')
    output += "\n\n### Confusion Matrix\n\n"
    output += confusion_matrix_to_text(result['confusion_matrix'])

print(output)