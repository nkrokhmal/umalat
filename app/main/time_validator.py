from wtforms.validators import ValidationError

from app.scheduler.time import *


def time_validator(form, field):
    wrong_input_msg = f'Неверный формат времени: {field.data}. Используйте формат типа "08:00". Если время указывается для предыдущего дня - формат типа "08:00-1". Если для последующего - формат типа "08:00+1" '
    try:
        cast_t(field.data)
        assert cast_human_time(field.data) == field.data
    except:
        raise ValidationError(wrong_input_msg)


def test():
    time_validator(None, utils.dotdict({"data": "7:00+1"}))


if __name__ == "__main__":
    test()
