
class GeneratorLimit(object):
    def __init__(self, gen, limit):
        self.gen = iter(gen)
        self.limit = limit

    def __len__(self):
        return self.limit

    def __iter__(self):
        return (next(self.gen) for i in range(self.limit))


class AttributeMapper(dict):
    """Helper class to map some dict values
    """
    def __init__(self, obj, mapping=None):
        self.obj = obj
        self.map = mapping if mapping is not None else dict()

    def __getitem__(self, k):
        if k in self.map:
            k = self.map[k]
        try:
            return self.obj[k]
        except KeyError:
            raise AttributeError

    def __str__(self):
        return '%s.%s(%s) <%s>' % (__name__, 'AttributeMapper', str(self.map), str(self.obj))


class RowWrapper:
    def __init__(self, obj, wrapper):
        self.obj = obj
        self.wrapper = wrapper

    def __iter__(self):
        return self

    def __next__(self):
        obj = next(self.obj)
        return self.wrapper(obj)

    def __len__(self):
        return self.obj.__len__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()