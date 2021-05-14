import os

os.environ["environment"] = "interactive"

from app.scheduler import *
from app.scheduler.mascarpone.boiling_plan.random import *
from app.scheduler.mascarpone.boiling_plan.random import (
    _generate_random_boiling_group,
)


def test():
    # print(_generate_random_boiling_group(MascarponeSKU, MascarponeBoiling))
    print(generate_random_boiling_plan())


if __name__ == "__main__":
    test()
