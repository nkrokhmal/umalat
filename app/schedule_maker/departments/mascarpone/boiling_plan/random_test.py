import os

os.environ["environment"] = "interactive"

from app.schedule_maker import *
from app.schedule_maker.departments.mascarpone.boiling_plan.random import *


def test():
    print(generate_random_boiling_plan())


if __name__ == "__main__":
    test()
