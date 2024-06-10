import re
import typing as tp

from utils_ak.numeric.types import is_int_like
from utils_ak.re.patterns import spaces_on_edge

from app.globals import db
from app.models.mozzarella import MozzarellaBoiling, MozzarellaFormFactor


def fetch_all(cls: tp.Any) -> tp.Any:
    return db.session.query(cls).all()


def query_exactly_one(cls: tp.Any, key: str, value: str | int | float) -> tp.Any:
    query = db.session.query(cls).filter(getattr(cls, key) == value)
    res = query.all()

    match len(res):
        case 0:
            raise Exception("Failed to fetch element {} {} {}".format(cls, key, value))
        case 1:
            return res[0]
        case _:
            return Exception("Fetched too many elements {} {} {}: {}".format(cls, key, value, res))


def cast_model(
    cls: tp.Any,
    obj: tp.Any,
    int_attribute: str = "id",
    str_attribute: str = "name",
) -> tp.Any:
    if isinstance(cls, list):
        results: list[tp.Any] = []
        for _cls in cls:
            try:
                results.append(cast_model(_cls, obj, int_attribute, str_attribute))
            except:
                ...
        assert len(results) == 1
        return results[0]

    elif isinstance(obj, cls):
        return obj
    elif is_int_like(obj):
        return query_exactly_one(cls, int_attribute, int(float(obj)))
    elif isinstance(obj, str):
        return query_exactly_one(cls, str_attribute, obj)
    else:
        raise Exception(f"Unknown {cls} type")


def cast_mozzarella_form_factor(obj):
    if isinstance(obj, str):
        # 'Вода: 200'
        # todo maybe: make 'Вода: 200' a default name for form factor, not 0.2 [@marklidenberg]
        short_line_name, relative_weight = obj.split(":")
        relative_weight = relative_weight.strip()
        short_line_names_map = {"Вода": "Моцарелла в воде", "Соль": "Пицца чиз"}

        form_factors = db.session.query(MozzarellaFormFactor).all()
        form_factors = [
            ff
            for ff in form_factors
            if str(ff.relative_weight) == relative_weight and ff.line.name == short_line_names_map[short_line_name]
        ]
        assert (
            len(form_factors) <= 1
        ), f"Найдены сразу несколько форм-факторов для форм-фактора плавления для {short_line_name} {relative_weight}"
        assert (
            len(form_factors) != 0
        ), f"Не найдено ни одного форм-фактора плавления для {short_line_name} {relative_weight}"
        return form_factors[0]
    else:
        return cast_model(MozzarellaFormFactor, obj)


def cast_mozzarella_boiling(obj):
    if isinstance(obj, str):
        try:

            # water, 2.7, Альче
            values = obj.split(",")
            line_name, percent, ferment = values[:3]
            percent = percent.replace(" ", "")
            ferment = re.sub(spaces_on_edge("beg"), "", ferment)
            ferment = re.sub(spaces_on_edge("end"), "", ferment)
            is_lactose = len(values) < 4
            query = db.session.query(MozzarellaBoiling).filter(
                (MozzarellaBoiling.percent == percent)
                & (MozzarellaBoiling.is_lactose == is_lactose)
                & (MozzarellaBoiling.ferment == ferment)
            )
            boilings = query.all()
            boilings = [b for b in boilings if b.line.name == line_name]
        except:
            raise Exception("Unknown boiling")

        if len(boilings) == 0:
            raise Exception(f"Boiling {obj} not found")
        elif len(boilings) > 1:
            raise Exception(f"Found multiple boilings {obj}")

        return boilings[0]

    return cast_model(MozzarellaBoiling, obj)
