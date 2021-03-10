import os

os.environ["environment"] = "interactive"

from app.schedule_maker.departments.ricotta.algo.cleanings import *


def test():
    print(make_bath_cleaning_sequence())


if __name__ == "__main__":
    test()
