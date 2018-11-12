class Dubbels:
    """
    Helper class to easily check which pids are duplicates of each other (loads data from dubbels.csv by default)
    """
    def __init__(self, file=None):
        if file is None:
            file = 'dubbels.csv'
        with open(file, 'r') as f:
            self.dubbels = [line.strip().split(',') for line in f]
        self.dubbels_lookup = dict()
        for idx, pids in enumerate(self.dubbels):
            for pid in pids:
                self.dubbels_lookup[pid] = idx

    def __contains__(self, k):
        return k in self.dubbels_lookup

    def __getitem__(self, k):
        if k not in self:
            raise AttributeError()
        result = self.dubbels[self.dubbels_lookup[k]]
        return [pid for pid in result if pid != k]

    def keys(self):
        return self.dubbels_lookup.keys()


def get_all_for_pid(pid, include_self=True):
    """
    Return all pids, including doubles, for given pid
    :param pid: str
    :return: list
    """
    dubbels = Dubbels()
    pid = pid.split('_', 1)
    if pid[0] in dubbels:
        pids = dubbels[pid[0]]
    else:
        pids = []
    if include_self:
        pids.append(pid[0])
    return ['%s_%s' % (p, pid[1]) for p in pids]
