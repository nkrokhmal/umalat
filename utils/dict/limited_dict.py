""" Dictionary with limited size. """

from utils_ak.dict import LastUsedOrderedDict


class LimitedDict(LastUsedOrderedDict):
    def __init__(self, max_size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = max_size

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        if self.max_size is not None and len(self) > self.max_size:
            while len(self) > self.max_size:
                self.popitem(last=False)


if __name__ == "__main__":

    d = LimitedDict(max_size=2)
    d["1"] = 1
    d["2"] = 2
    print(d.pick("1"))
    d["3"] = 3
    print(d)
