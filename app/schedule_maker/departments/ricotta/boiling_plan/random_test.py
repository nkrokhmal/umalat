import os

os.environ["environment"] = "interactive"

from app.schedule_maker import *
from app.schedule_maker.departments.ricotta.boiling_plan.random import *


def test():
    import random

    random.seed(12)
    print(generate_random_boiling_plan())


if __name__ == "__main__":
    test()
