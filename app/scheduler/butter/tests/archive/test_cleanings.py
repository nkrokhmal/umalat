import os


os.environ["APP_ENVIRONMENT"] = "interactive"


def test():
    print(make_bath_cleanings())


if __name__ == "__main__":
    test()
