from pythonmodules.ner import NERFactory
import sys
import difflib

if '--help' in sys.argv:
    print('usage: %s [nerclass] text')
    print(' nerclass: (optional) name of the class to use for NER, eg. StanfordNER, or "compare"')
    print('     to compare results of all known taggers')
    print(' text: the text to tag')
    exit(0)

if len(sys.argv) < 2:
    print('text argument is required')
    exit(1)

conf = sys.argv[1] if len(sys.argv) > 2 else None
text = sys.argv[-1]
if conf != 'compare':
    ner = NERFactory().get(conf)
    print(ner.tag(text))
    exit(0)


results = {}
for class_name in NERFactory.KNOWN_TAGGERS:
    results[class_name] = NERFactory().get(class_name).tag(text)

base_key = next(iter(results))
base = results[base_key]
del results[base_key]
for cls in results:
    other = results[cls]
    print('')
    print('%s vs %s:' % (base_key, cls))
    print("\n".join([line for line in difflib.Differ().compare(base, other) if line[0] in '-+']))
    print('')
