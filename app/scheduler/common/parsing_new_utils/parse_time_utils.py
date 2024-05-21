from app.scheduler.common.time_utils import cast_time, parse_time


def cast_time_from_hour_label(hour_label):
    if "-" in hour_label:
        splitter = "-"
        split = hour_label.split("-")
    elif "+" in hour_label:
        splitter = "+"
        split = hour_label.split("+")
    else:
        splitter = ""
        split = [hour_label, ""]

    return cast_time(split[0] + ":00" + splitter + split[-1])


def cast_label_from_time(label_time):
    days, hours, minutes = parse_time(label_time)  # '23:00+1
    res = str(hours)
    if days > 0:
        res += "+" + str(abs(days))
    elif days < 0:
        res += "-" + str(abs(days))
    return res


def test():
    assert cast_time_from_hour_label("23") == "0:23:00"
    assert cast_time_from_hour_label("23+1") == "1:23:00"
    assert cast_time_from_hour_label("23-1") == "-1:23:00"
    print(cast_label_from_time("23:00+1"))
    print(cast_label_from_time("23:00-1"))
    print(cast_label_from_time("23:00"))


if __name__ == "__main__":
    test()
