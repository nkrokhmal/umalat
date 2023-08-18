import os


os.environ["APP_ENVIRONMENT"] = "interactive"

from app.scheduler.ricotta.algo.cleanings import *


def test():
    print(make_bath_cleanings())


if __name__ == "__main__":
    test()
