import datetime

def cast_t(obj):
    if isinstance(obj, int):
        return obj
    elif isinstance(obj, datetime.time):
        return cast_t(cast_time(obj))
    elif isinstance(obj, str):
        # 3:12:00
        if obj.count(':') == 1:
            hours, minutes = obj.split(':')
            days = 0
        elif obj.count(':') == 2:
            days, hours, minutes = obj.split(':')
        else:
            raise Exception('Unknown format')
        minutes = int(days) * 288 * 5 + int(hours) * 60 + int(minutes)
        assert minutes % 5 == 0
        return minutes // 5
    else:
        raise Exception('Unknown format')


def cast_time(obj):
    if isinstance(obj, str):
        if obj.count(':') == 1:
            return '0:' + obj
        else:
            return obj
    elif isinstance(obj, datetime.time):
        return cast_time(f'0:{obj.hour}:{obj.minute}')
    elif isinstance(obj, int):
        days = obj // 288
        hours = (obj // 12) % 24
        minutes = (obj % 12) * 5
        return f'{days:02}:{hours:02}:{minutes:02}'


def test():
    print(cast_t('1:23:55'))
    print(cast_t('0:23:55'))
    print(cast_t('-1:23:55'))
    print(cast_time(1))
    print(cast_time(0))
    print(cast_time(-1))


if __name__ == '__main__':
    test()