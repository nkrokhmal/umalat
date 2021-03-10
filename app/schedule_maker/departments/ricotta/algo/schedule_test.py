import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.ricotta.algo.schedule import *


def test():
    print(make_schedule())


if __name__ == "__main__":
    test()
