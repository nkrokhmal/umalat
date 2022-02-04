from app.imports.runtime import *

"""
Formats
time: [-]1:23:55 
human_time: 23:55 or 23:55[+-]1 
t: 575
"""


def cast_t(obj):
    with code("Handle None"):
        if obj == 0:
            return 0
        if utils.is_none(obj) or not obj:
            return None

    if utils.is_int_like(obj):
        return int(obj)
    elif isinstance(obj, (tuple, list)) and all(utils.is_int_like(v) for v in obj):
        days, hours, minutes = obj # unpack
        days, hours, minutes = list(map(int, (days, hours, minutes))) # convert to int
        total_minutes = int(days) * 288 * 5 + int(hours) * 60 + int(minutes)
        assert total_minutes % 5 == 0
        return total_minutes // 5
    elif isinstance(obj, time):
        return cast_t((0, obj.hour, obj.minute))
    elif isinstance(obj, str):
        if obj.count(":") == 1:
            # human time format: 23:55+1
            if "-" in obj:
                obj, days = obj.split("-")
                days = -int(days)
            elif "+" in obj:
                obj, days = obj.split("+")
            else:
                days = 0
            hours, minutes = obj.split(":")
        elif obj.count(":") == 2:
            # classic time format: 1:23:55
            days, hours, minutes = obj.split(":")
        else:
            raise Exception(f"Unknown format: {obj}")
        return cast_t((days, hours, minutes))
    else:
        raise Exception("Unknown format: {} {}".format(type(obj), obj))


def is_none(obj):
    return cast_t(obj) is None


def cast_time(obj):
    if is_none(obj):
        return None

    days, hours, minutes = parse_time(obj)
    return f"{days}:{hours:02}:{minutes:02}"


def cast_human_time(obj):
    if is_none(obj):
        return None

    days, hours, minutes = parse_time(obj)
    if days == 0:
        return ':'.join(cast_time(obj).split(':')[1:])
    else:
        sign = "+" if days > 0 else "-"
        return f"{hours:02}:{minutes:02}{sign}{abs(days)}"


def parse_time(time_obj):
    t = cast_t(time_obj)
    days = t // 288
    hours = (t // 12) % 24
    minutes = (t % 12) * 5
    return days, hours, minutes


def test():
    for value in ['1:23:55', '0:23:55', '-1:23:55', 1, 0, -1, '08:00', '0:08:00', '21:35-1', '10:08:00']:
        assert cast_t(value) == cast_t(cast_time(cast_t(value)))
        assert cast_t(value) == cast_t(cast_human_time(cast_t(value)))
        assert cast_time(value) == cast_time(cast_t(cast_time(value)))
        print()
        print(value)
        print(cast_t(value))
        print(cast_time(value))
        print(cast_human_time(value))

    for wrong_value in ['a:08:00', '08:0a']:
        try:
            cast_time(wrong_value)
        except Exception:
            pass
        else:
            raise Exception('Should not happen')


if __name__ == "__main__":
    test()
