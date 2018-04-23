from django.core.cache.backends.filebased import FileBasedCache
import sys, os

if __name__ != '__main__':
  raise Exception("Meant to be ran as quick helper script")

if len(sys.argv) != 2:
   print("Usage:\n\t%s directory|file")
   raise Exception("Expected 1 argument")

c = FileBasedCache(os.path.dirname(sys.argv[1]), {})
c._key_to_file = lambda key, version: key

for f in sys.argv[1:]:
   print('%s:' % f)
   if os.path.isdir(f):
      print("\n".join(c._list_cache_files()))
   else:
      print(c.get(f))
