import datetime
import re

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
            assert re.search(r'(\d\d):(\d\d)', obj)
            return '0:' + obj
        else:
            assert re.search(r'(\d+):(\d\d):(\d\d)', obj)
            return obj
    elif isinstance(obj, datetime.time):
        return cast_time('0:' + str(obj.hour).zfill(2) + ':' + str(obj.minute).zfill(2))
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

    try:
        print(cast_time('08:00'))
        print(cast_time('08:0a'))
    except AssertionError:
        print('Wrong format')

    try:
        print(cast_time('0:08:00'))
        print(cast_time('a:08:00'))
    except AssertionError:
        print('Wrong format')


if __name__ == '__main__':
    test()