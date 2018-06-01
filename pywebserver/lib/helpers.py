
class GeneratorLimit(object):
    def __init__(self, gen, limit):
        self.gen = gen
        self.limit = limit

    def __len__(self):
        return self.limit

    def __iter__(self):
        return (next(self.gen) for i in range(self.limit))
