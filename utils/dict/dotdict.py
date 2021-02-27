""" Dictionary with dot as a level separator. """
from utils_ak.serialization import js as json


def is_dict_instance(obj):
    """
    Return if provided object is type of dict or instance of DotDict class
    """
    return isinstance(obj, dict) or isinstance(obj, dotdict)


class dotdict(dict):
    def __init__(self, dic=None, as_default_dict=False):
        super().__init__()

        if dic is not None and not is_dict_instance(dic):
            raise Exception("Bad dic input")

        self._as_default_dict = as_default_dict

        if dic is not None:
            for k, v in dic.items():
                if is_dict_instance(v):
                    self[k] = self._cls(v)
                else:
                    self[k] = v

    @property
    def sys_attrs(self):
        return ["_as_default_dict", "_dic"]

    def __delattr__(self, item):
        return self.__delitem__(item)

    def _cls(self, dic=None):
        """ Inherit parent class. """
        return dotdict(dic, as_default_dict=self._as_default_dict)

    def __setattr__(self, key, value):
        if key not in self.sys_attrs:
            self[key] = value
        else:
            super().__setattr__(key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        if key in self.sys_attrs:
            return super().__getitem__(key)

        if key in self or self._as_default_dict:
            return self.get(key)
        raise KeyError(key)

    def __setitem__(self, key, val):
        self._set(key, val)

    def __contains__(self, key):
        split_keys = self._split_key(key)

        first = split_keys[0]

        if len(split_keys) == 1:
            return super().__contains__(key)

        if not super().__contains__(first) or not is_dict_instance(self[first]):
            return False

        return ".".join(split_keys[1:]) in self[first]

    def _set(self, key, value):
        obj = self

        split_keys = self._split_key(key)

        for key in split_keys[:-1]:
            obj = obj.setdefault(key, self._cls())
            if not is_dict_instance(obj):
                raise Exception("Cannot assign new value, internal obj is not dict")

        if len(split_keys) == 1:
            super().__setitem__(split_keys[-1], value)
        else:
            obj._set(split_keys[-1], value)

        # obj.__setitem__(split_keys[-1], value)

    def delete(self, key):
        """
        Delete provided compound key from `dotdict`
        """
        obj = self
        split_keys = key.split(".")
        for key in split_keys:
            if key == split_keys[-1]:
                del obj[key]
                break
            if isinstance(obj, dotdict):
                obj = self.__getitem__(key)
            else:
                obj = obj.__getitem__(key)

    def get(self, key, default=None):
        """
        Get value for provided compound key. In a case of accessed value of a list type returns its first element.
        """
        split_keys = self._split_key(key)
        first = split_keys[0]

        if first in self:
            obj = super().__getitem__(first)

            if first == key:
                # no dotted notation used
                return obj

            if is_dict_instance(obj):
                return obj.get(".".join(split_keys[1:]))
            else:
                return default
        else:
            if self._as_default_dict:
                return self.setdefault(first, self._cls())
            else:
                return default

    def __getstate__(self):
        return dict(self)

    def copy(self):
        return self._cls(self)

    @staticmethod
    def _split_key(key):
        if hasattr(key, "split"):
            return key.split(".")
        return [key]


if __name__ == "__main__":
    dd = dotdict({0: 1})

    print(dd[0])

    dd = dotdict({"a": {"b": 1, "c": [1, 2]}}, as_default_dict=False)
    print(dd)
    print(dict(dd))
    print(dd["a.c"])
    print(dd.get("a.c.does_not_exist"))

    try:
        dd["a.c.does_not_exist"]
    except KeyError as e:
        print("error", e)

    dd["x.y.z"] = 1
    print(dd)
    print(dd.x.y.z)

    import collections

    print(isinstance(dd, collections.Mapping))

    print(dd.a["c"])

    """
    Output:
    {'a': {'b': 1, 'c': [1, 2]}}
        {'a': {'b': 1, 'c': [1, 2]}}
        [1, 2]
        None
        error 'c'
        {'a': {'b': 1, 'c': [1, 2]}, 'x': {'y': {'z': 1}}}
        1
        True
        [1, 2]
        """

    import pickle

    print(pickle.dumps(dd))

    dd = dotdict(as_default_dict=True)
    dd["d"]["e"]["f.g"] = 1
    print(dd)

    dd.foo.bar = 2
    print(dd)

    print(json.dumps(dd))

    from collections import Mapping

    print(isinstance(dd, Mapping))

    import pickle

    print(pickle.dumps(dd))
