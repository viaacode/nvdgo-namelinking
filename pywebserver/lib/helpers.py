
class GeneratorLimit(object):
    def __init__(self, gen, limit: int):
        self.gen = iter(gen)
        self.limit = limit

    def __len__(self):
        return self.limit

    def __iter__(self):
        return (next(self.gen) for i in range(self.limit))


class GeneratorSkip(object):
    def __init__(self, gen, offset: int):
        self.gen = iter(gen)
        self.offset = offset

    def __len__(self):
        return len(self.gen) - self.offset

    def __iter__(self):
        for i, item in enumerate(self.gen):
            if i < self.offset:
                continue
            yield next(self.gen)


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

    def __contains__(self, k):
        if k in self.map:
            k = self.map[k]

        return k in self.obj

    def __str__(self):
        return '%s.%s(%s) <%s>' % (__name__, 'AttributeMapper', str(self.map), str(self.obj))


class RowWrapper:
    def __init__(self, obj, wrapper):
        self.obj = obj
        self.length = None
        if type(obj) is list:
            self.length = len(obj)
            self.obj = iter(self.obj)
        self.wrapper = wrapper

    def __iter__(self):
        return self

    def __next__(self):
        obj = next(self.obj)
        return self.wrapper(obj)

    def __len__(self):
        if self.length is None:
            return self.obj.__len__()
        return self.length


if __name__ == '__main__':
    import doctest
    doctest.testmod()
