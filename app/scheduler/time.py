from app.imports.runtime import *


def cast_t(obj):
    if obj is None:
        return None
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, time):
        return cast_t(cast_time(obj))
    elif isinstance(obj, str):
        # 3:12:00
        if obj.count(":") == 1:
            if "-" in obj:
                obj, days = obj.split("-")
                days = -int(days)
            elif "+" in obj:
                obj, days = obj.split("+")
            else:
                days = 0
            hours, minutes = obj.split(":")

        elif obj.count(":") == 2:
            days, hours, minutes = obj.split(":")
        else:
            raise Exception(f"Unknown format: {obj}")
        minutes = int(days) * 288 * 5 + int(hours) * 60 + int(minutes)
        assert minutes % 5 == 0
        return minutes // 5
    else:
        raise Exception("Unknown format")


def cast_time(obj):
    if isinstance(obj, str):
        days = 0
        if "-" in obj:
            obj, days = obj.split("-")
            days = -int(days)
        elif "+" in obj:
            obj, days = obj.split("+")
            days = int(days)

        if obj.count(":") == 1:
            assert re.search(r"(\d\d):(\d\d)", obj)
            return f"{days}:" + obj
        else:
            assert re.search(r"(\d+):(\d\d):(\d\d)", obj)
            return obj
    elif isinstance(obj, time):
        return cast_time("0:" + str(obj.hour).zfill(2) + ":" + str(obj.minute).zfill(2))
    elif utils.is_int_like(obj):
        obj = int(obj)
        days = obj // 288
        hours = (obj // 12) % 24
        minutes = (obj % 12) * 5
        return f"{days:02}:{hours:02}:{minutes:02}"


def cast_human_time(obj):
    t = cast_t(obj)
    days = t // 288
    hours = (t // 12) % 24
    minutes = (t % 12) * 5

    if days == 0:
        return cast_time(t)[3:]
    else:
        sign = "+" if days > 0 else "-"
        return f"{hours:02}:{minutes:02}{sign}{abs(days)}"


def test():
    print(cast_t("1:23:55"))
    print(cast_t("0:23:55"))
    print(cast_t("-1:23:55"))
    print(cast_time(1))
    print(cast_time(0))
    print(cast_time(-1))

    try:
        print(cast_time("08:00"))
        print(cast_time("08:0a"))
    except AssertionError:
        print("Wrong format")

    try:
        print(cast_time("0:08:00"))
        print(cast_time("a:08:00"))
    except AssertionError:
        print("Wrong format")

    print(cast_time("21:35-1"))
    print(cast_t("21:35-1"))

    print(cast_human_time(-1))
    print(cast_human_time("21:35"))
    print(cast_human_time("1:21:35"))
    print(cast_human_time("-1:21:35"))


if __name__ == "__main__":
    test()
