from collections import OrderedDict


class LastUsedOrderedDict(OrderedDict):
    """Store items in the order the keys were last added"""

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        super().__setitem__(key, value)

    def pick(self, key):
        self.__setitem__(key, self[key])
        return self[key]


if __name__ == '__main__':
    d = LastUsedOrderedDict()
    d['1'] = 1
    d['2'] = 2
    print(d)
    print(d.pick('1'))
    print(d)
    d['2'] = 3
    print(d)
