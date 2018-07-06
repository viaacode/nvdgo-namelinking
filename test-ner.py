from pythonmodules.ner import NERFactory
import sys
import random
from pythonmodules.profiling import timeit

if '--help' in sys.argv:
    print('usage: %s [--compare] [--write] text-or-file|--random-mediahaven')
    print(' text-or-file: the text to tag, ')
    print('        or "--random-mediahaven" to get a random OCR description from a MediaHaven newspaper')
    exit(0)

if len(sys.argv) < 2:
    print('text argument is required')
    exit(1)
args = list(sys.argv[1:])
text = args.pop()
print(args)
print(text)

try:
    with open(text, 'r') as f:
        text = "\n".join([line for line in f])
except FileNotFoundError:
    print('FileNotFound, using text')
    pass

if text == '--random-mediahaven':
    from pythonmodules.mediahaven import MediaHaven
    q = '+(workflow:GMS) +(archiveStatus:on_tape) +(externalId:k06ww78d74_19140202_0004)'
    mh = MediaHaven()
    search = mh.search(q)
    print('%d possible documents found' % len(search))
    text = ''
    while len(text) == 0:
        idx = random.randint(0, len(search) - 1)
        # idx = 210030
        item = mh.one(q, startIndex=idx)
        text = item['description']
        print('Using description from %s (#%d)' % (item['externalId'], idx))
    with open('test.txt', 'w') as f:
        f.write(text)


if '--compare' not in args:
    ner = NERFactory().get()
    print(ner.tag(text))
    exit(0)


results = {}
times = {}
timer = timeit()
for class_name in NERFactory.KNOWN_TAGGERS:
    timer.restart()
    results[class_name] = NERFactory().get(class_name).tag(text)
    times[class_name] = timer.elapsed()

base_key = next(iter(results))
base = results[base_key]
del results[base_key]
if '--write' in args:
    with open(base_key + '-results.txt', 'w') as f:
        f.writelines([str(line) + "\n" for line in base])

print('Base for comparison: %s' % base_key)

for cls in results:
    other = results[cls]

    if '--write' in args:
        with open(cls + '-results.txt', 'w') as f:
            f.writelines([str(line) + "\n" for line in other])

    base_types = [row[1] for row in base]
    other_types = [row[1] for row in other]
    if len(base) != len(other):
        print('Difference in length %s %d vs. %s %d' % (base_key, len(base), cls, len(other)))
        continue
    diffs = []

    for idx, val in enumerate(base):
        word1, type1 = val
        word2, type2 = other[idx]
        if type1 != type2:
            diffs.append('#%6d %s got %s, expected %s for: "%s" / "%s"' % (idx, cls, type2, type1, word2, word1))
    print('%s vs %s: %d differences of %d lines (%.2f%%)' % (base_key, cls, len(diffs), len(base), len(diffs)/len(base)))
    for line in diffs:
        print(line)

print("Runtimes:")
for k in times:
    print(' %s %dms' % (k, times[k]))