from app.imports.runtime import *


def test_notifier():
    notifier = Notifier()
    notifier.notify("Topic", "Message")
    notifier.notify("Topic", "Message", urgency=5)
    notifier.notify("Topic", "Message", urgency=12)


if __name__ == "__main__":
    test_notifier()
