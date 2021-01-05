import datetime
def cast_t(obj):
    if isinstance(obj, int):
        return obj
    elif isinstance(obj, datetime.time):
        return cast_t(cast_time(obj))
    elif isinstance(obj, str):
        # 12:00
        hours, minutes = obj.split(':')
        minutes = int(hours) * 60 + int(minutes)
        assert minutes % 5 == 0
        return minutes // 5
    else:
        raise Exception('Unknown format')


def cast_time(obj):
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, datetime.time):
        return cast_time(f'{obj.hour}:{obj.minute}')
    elif isinstance(obj, int):
        hours = obj // 12
        hours = hours % 24
        minutes = obj % 12 * 5
        return f'{hours:02}:{minutes:02}'


if __name__ == '__main__':
    print(cast_t('12:00'))
    print(cast_time(145))