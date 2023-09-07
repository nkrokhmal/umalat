from itertools import count


def test():
    count()  # 0,1,2,3,4, ...
    count(start=2, step=2)  # 2,4,6, ...


if __name__ == "__main__":
    test()
