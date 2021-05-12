import os

os.environ["environment"] = "interactive"

from app.scheduler import *
from app.scheduler.ricotta.boiling_plan.random import *


def test():
    print(generate_random_boiling_plan())


if __name__ == "__main__":
    test()
