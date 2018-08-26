from django.core.cache.backends.filebased import FileBasedCache
import sys, os

# quick script to get all externalIds that are cached:
# `python read_cache.py /tmp/pywebserver_cache/mediahaven | xargs python read_cache.py | grep externalId --color | \
#  sed 's/^.*externalId.: .\(........................\).*$/\1/g'`

if __name__ != '__main__':
    raise Exception("Meant to be ran as quick helper script")

if len(sys.argv) < 2:
    print("Usage:\n\t%s directory|file1[, file2, ...]")
    raise Exception("Expected 1 argument")

dir = sys.argv[1] if os.path.isdir(sys.argv[1]) else os.path.dirname(sys.argv[1])
c = FileBasedCache(dir, {})
c._key_to_file = lambda key, version: key

for f in sys.argv[1:]:
    if os.path.isdir(f):
        if not os.path.exists(f):
           raise NotADirectoryError('Unknown path %s' % f)
        print("\n".join(c._list_cache_files()))
    else:
        print(c.get(f))
