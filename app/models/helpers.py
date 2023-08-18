from app.enum import LineName
from app.imports.runtime import *

from .mozzarella import MozzarellaBoiling, MozzarellaFormFactor


def fetch_all(cls):
    return db.session.query(cls).all()


def query_exactly_one(cls, key, value):
    query = db.session.query(cls).filter(getattr(cls, key) == value)
    res = query.all()

    if len(res) == 0:
        raise Exception("Failed to fetch element {} {} {}".format(cls, key, value))
    elif len(res) > 1:
        raise Exception("Fetched too many elements {} {} {}: {}".format(cls, key, value, res))
    else:
        return res[0]


def cast_model(cls, obj, int_attribute="id", str_attribute="name"):
    if isinstance(cls, list):
        results = []
        for _cls in cls:
            try:
                results.append(cast_model(_cls, obj, int_attribute, str_attribute))
            except:
                pass
        assert len(results) == 1
        return results[0]

    elif isinstance(obj, cls):
        return obj
    elif utils.is_int_like(obj):
        return query_exactly_one(cls, int_attribute, int(float(obj)))
    elif isinstance(obj, str):
        return query_exactly_one(cls, str_attribute, obj)
    else:
        raise Exception(f"Unknown {cls} type")


def cast_mozzarella_form_factor(obj):
    if isinstance(obj, str):
        # 'Вода: 200'
        # todo maybe: make 'Вода: 200' a default name for form factor, not 0.2.
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
            ferment = re.sub(utils.spaces_on_edge("beg"), "", ferment)
            ferment = re.sub(utils.spaces_on_edge("end"), "", ferment)
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
