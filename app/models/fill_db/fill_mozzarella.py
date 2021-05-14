from ...enum import LineName
import pandas as pd
import json
from app.models import *


def read_params(fn="app/data/static/params/mozzarella.xlsx"):
    df = pd.read_excel(fn, index_col=0)
    return df


def fill_db():
    fill_boiling_technologies()
    # fill_cooling_technologies()
    fill_boilings()
    fill_form_factors()
    fill_sku()
    fill_form_factors_made_from()
    fill_steam_consumption()


def fill_boiling_technologies():
    df = read_params()
    boiling_technologies_columns = [
        "Время налива",
        "Время отвердевания",
        "Время нарезки",
        "Время слива",
        "Дополнительное время",
        "Линия",
        "Процент",
        "Откачка",
        "Наличие лактозы",
        "Тип закваски",
    ]
    bt_data = df[boiling_technologies_columns]
    bt_data["Наличие лактозы"] = bt_data["Наличие лактозы"].apply(
        lambda x: True if x == "Да" else False
    )
    bt_data = bt_data.drop_duplicates()
    bt_data = bt_data.to_dict("records")
    for bt in bt_data:
        line_name = LineName.SALT if bt["Линия"] == "Соль" else LineName.WATER
        technology = MozzarellaBoilingTechnology(
            name=MozzarellaBoilingTechnology.create_name(
                line=line_name,
                percent=bt["Процент"],
                ferment=bt["Тип закваски"],
                is_lactose=bt["Наличие лактозы"],
            ),
            pouring_time=bt["Время налива"],
            soldification_time=bt["Время отвердевания"],
            cutting_time=bt["Время нарезки"],
            pouring_off_time=bt["Время слива"],
            pumping_out_time=bt["Откачка"],
            extra_time=bt["Дополнительное время"],
        )

        db.session.add(technology)
        db.session.commit()


def fill_cooling_technologies():
    df = read_params()
    data = df[
        [
            "Название форм фактора",
            "Вес форм фактора",
            "Охлаждение 1(для воды)",
            "Охлаждение 2(для воды)",
            "Время посолки",
            "Линия",
        ]
    ]
    data = data.drop_duplicates()
    data = data.to_dict("records")
    for value in data:
        if any([not np.isnan(x) for x in value.values()]):
            technology = MozzarellaCoolingTechnology(
                first_cooling_time=value["Охлаждение 1(для воды)"],
                second_cooling_time=value["Охлаждение 2(для воды)"],
                salting_time=value["Время посолки"],
            )

            db.session.add(technology)
    db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(MozzarellaBoilingTechnology).all()
    columns = [
        "Тип закваски",
        "Процент",
        "Наличие лактозы",
        "Линия",
        "Время налива",
        "Время отвердевания",
        "Время нарезки",
        "Время слива",
        "Дополнительное время",
    ]
    b_data = df[columns]
    b_data["Наличие лактозы"] = b_data["Наличие лактозы"].apply(
        lambda x: True if x == "Да" else False
    )
    b_data = b_data.drop_duplicates()
    b_data = b_data.to_dict("records")
    for b in b_data:
        line_name = LineName.SALT if b["Линия"] == "Соль" else LineName.WATER
        if b["Линия"] == "Соль":
            line_id = [x for x in lines if x.name == LineName.SALT][0].id
        else:
            line_id = [x for x in lines if x.name == LineName.WATER][0].id
        bts_name = [
            x
            for x in bts
            if (x.pouring_time == b["Время налива"])
            & (x.soldification_time == b["Время отвердевания"])
            & (x.cutting_time == b["Время нарезки"])
            & (x.pouring_off_time == b["Время слива"])
            & (x.extra_time == b["Дополнительное время"])
            & (
                x.name
                == MozzarellaBoilingTechnology.create_name(
                    line=line_name,
                    percent=b["Процент"],
                    ferment=b["Тип закваски"],
                    is_lactose=b["Наличие лактозы"],
                )
            )
        ]
        boiling = MozzarellaBoiling(
            percent=b["Процент"],
            is_lactose=b["Наличие лактозы"],
            ferment=b["Тип закваски"],
            boiling_technologies=bts_name,
            line_id=line_id,
        )
        db.session.add(boiling)
        db.session.commit()


def fill_form_factors():
    lines = db.session.query(Line).all()
    df = read_params()
    mass_ff = MozzarellaFormFactor(name="Масса")
    db.session.add(mass_ff)
    db.session.commit()

    columns = [
        "Название форм фактора",
        "Вес форм фактора",
        "Охлаждение 1(для воды)",
        "Охлаждение 2(для воды)",
        "Время посолки",
        "Линия",
    ]
    df = df[columns]
    df["Название форм фактора"] = df.apply(
        lambda x: x["Название форм фактора"] if x["Вес форм фактора"] == 1 else None,
        axis=1,
    )
    df = df.drop_duplicates()
    values = df.to_dict("records")
    for value in values:
        line_name = LineName.SALT if value["Линия"] == "Соль" else LineName.WATER
        if value["Вес форм фактора"] == 1:
            name = "Терка {}".format(value["Название форм фактора"])
        elif (
            (value["Вес форм фактора"] == 7.5)
            or (value["Вес форм фактора"] == 15)
            or (value["Вес форм фактора"] == 30)
        ):
            name = "Палочки {}г".format(value["Вес форм фактора"])
        else:
            name = str(value["Вес форм фактора"] / 1000)

        form_factor = MozzarellaFormFactor(
            name=name, relative_weight=value["Вес форм фактора"]
        )
        form_factor.line = [x for x in lines if x.name == line_name][0]
        # cooling_technologies = db.session.query(MozzarellaCoolingTechnology).all()
        if "Терка" not in name:
            cooling_technology = MozzarellaCoolingTechnology(
                first_cooling_time=value["Охлаждение 1(для воды)"],
                second_cooling_time=value["Охлаждение 2(для воды)"],
                salting_time=value["Время посолки"],
            )
            db.session.add(cooling_technology)
            db.session.commit()
            form_factor.default_cooling_technology = cooling_technology
        db.session.add(form_factor)
    db.session.commit()
    form_factors = db.session.query(MozzarellaFormFactor).all()
    mass_ff = [x for x in form_factors if x.name == "Масса"][0]
    for form_factor in form_factors:
        form_factor.add_made_from(form_factor)
        form_factor.add_made_from(mass_ff)
    db.session.commit()


def _cast_non_nan(obj):
    if obj is None:
        return
    elif np.isnan(obj):
        return
    else:
        return obj


def fill_sku():
    df = read_params()
    lines = db.session.query(MozzarellaLine).all()
    packer = db.session.query(Packer).all()
    boilings = db.session.query(MozzarellaBoiling).all()
    form_factors = db.session.query(MozzarellaFormFactor).all()
    groups = db.session.query(Group).all()

    columns = [
        "Название SKU",
        "Процент",
        "Наличие лактозы",
        "Тип закваски",
        "Имя бренда",
        "Вес нетто",
        "Срок хранения",
        "Коробки",
        "Является ли SKU теркой",
        "Упаковщик",
        "Скорость упаковки",
        "Скорость сборки",
        "Линия",
        "Вес форм фактора",
        "Название форм фактора",
        "Охлаждение 1(для воды)",
        "Охлаждение 2(для воды)",
        "Время посолки",
    ]

    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict("records")
    for sku in sku_data:

        is_lactose = sku["Наличие лактозы"] == "Да"
        add_sku = MozzarellaSKU(
            name=sku["Название SKU"],
            brand_name=sku["Имя бренда"],
            weight_netto=sku["Вес нетто"],
            shelf_life=sku["Срок хранения"],
            collecting_speed=_cast_non_nan(sku["Скорость сборки"])
            or _cast_non_nan(sku["Скорость упаковки"]),
            packing_speed=sku["Скорость упаковки"],
            in_box=sku["Коробки"],
        )

        sku_packers = [x for x in packer if x.name in sku["Упаковщик"].split("/")]
        add_sku.packers += sku_packers

        line_name = LineName.SALT if sku["Линия"] == "Соль" else LineName.WATER
        add_sku.line = [x for x in lines if x.name == line_name][0]

        add_sku.made_from_boilings = [
            x
            for x in boilings
            if (x.percent == sku["Процент"])
            & (x.is_lactose == is_lactose)
            & (x.ferment == sku["Тип закваски"])
            & (x.line_id == add_sku.line.id)
        ]
        add_sku.group = [x for x in groups if x.name == sku["Название форм фактора"]][0]
        if add_sku.group.name != "Качокавалло":
            add_sku.production_by_request = True
            add_sku.packing_by_request = True
        elif add_sku.name == 'Качокавалло "Unagrande", 45%, 0,26 кг, в/у, (8 шт)':
            add_sku.production_by_request = False
            add_sku.packing_by_request = True
        else:
            add_sku.production_by_request = False
            add_sku.packing_by_request = False
        if sku["Вес форм фактора"] != 1:
            add_sku.form_factor = [
                x
                for x in form_factors
                if x.relative_weight == sku["Вес форм фактора"]
                and x.line.name == line_name
            ][0]
        else:
            add_sku.form_factor = [
                x
                for x in form_factors
                if x.name == "Терка {}".format(sku["Название форм фактора"])
            ][0]

        db.session.add(add_sku)
    db.session.commit()


def fill_form_factors_made_from():
    skus = db.session.query(MozzarellaSKU).all()
    form_factors = db.session.query(MozzarellaFormFactor).all()
    sul_ff = [x for x in form_factors if x.name == "Терка Сулугуни"][0]
    moz_ff = [x for x in form_factors if x.name == "Терка Моцарелла"][0]
    sul_ffs = set(
        [
            x.form_factor
            for x in skus
            if "сулугуни" in x.name.lower() and x.line.name == LineName.SALT
        ]
    )
    moz_ffs = set(
        [
            x.form_factor
            for x in skus
            if "моцарелла" in x.name.lower() and x.line.name == LineName.SALT
        ]
    )
    for sul in sul_ffs:
        sul_ff.add_made_from(sul)
    for moz in moz_ffs:
        moz_ff.add_made_from(moz)
    db.session.commit()


def fill_steam_consumption():
    lines = db.session.query(Line).all()
    water_params = {
        "boiling": {
            "pouring": {
                "time": 25,
                "steam_consumption": 1100,
                "start_from_beginning": True,
            }
        },
        "melting": {
            "beg": {
                "time": 25,
                "steam_consumption": 300,
                "start_from_beginning": False,
            },
            "melting": {
                "time": 0,
                "steam_consumption": 250,
                "start_from_beginning": True,
            },
        },
    }
    salt_params = {
        "boiling": {
            "pouring": {
                "time": 25,
                "steam_consumption": 1100,
                "start_from_beginning": True,
            },
            "cutting": {
                "time": 15,
                "steam_consumption": 700,
                "start_from_beginning": False,
            },
        },
        "melting": {
            "beg": {
                "time": 25,
                "steam_consumption": 2000,
                "start_from_beginning": False,
            },
            "melting": {
                "time": 0,
                "steam_consumption": 1200,
                "start_from_beginning": True,
            },
        },
    }
    for line in lines:
        if line.name == LineName.SALT:
            steam_consumption = SteamConsumption(
                params=json.dumps(salt_params),
            )
        else:
            steam_consumption = SteamConsumption(
                params=json.dumps(water_params),
            )
        steam_consumption.line = line
        db.session.add(steam_consumption)
        db.session.commit()
