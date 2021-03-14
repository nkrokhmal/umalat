import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.mascarpone.algo.cleanings import *


def test():
    print(make_cleaning("separator"))


if __name__ == "__main__":
    test()
