import os

import flask
import flask_login
import pandas as pd

from app.globals import db
from app.main import main
from app.models.mozzarella import MozzarellaSKU


@main.route("/download_mozzarella", methods=["POST", "GET"])
@flask_login.login_required
def download_mozzarella():
    skus = db.session.query(MozzarellaSKU).all()
    data = [
        {
            "Название SKU": sku.name,
            "Процент": sku.made_from_boilings[0].percent,
            "Наличие лактозы": "Да" if sku.made_from_boilings[0].is_lactose else "Нет",
            "Название форм фактора": sku.group.name,
            "Линия": "Соль" if sku.line.name == "Пицца чиз" else "Вода",
            "Тип закваски": sku.made_from_boilings[0].ferment,
            "Имя бренда": sku.brand_name,
            "Вес нетто": sku.weight_netto,
            "Коробки": sku.in_box,
            "Вес форм фактора": sku.form_factor.relative_weight,
            "Выход": sku.line.output_kg,
            "Срок хранения": sku.shelf_life,
            "Является ли SKU теркой": "Да" if "Терка" in sku.form_factor.name else "Нет",
            "Упаковщик": "/".join([packer.name for packer in sku.packers]),
            "Тип упаковки": "",
            "Скорость сборки": sku.collecting_speed,
            "Скорость упаковки": sku.packing_speed,
            "Охлаждение 1(для воды)": ""
            if not sku.form_factor.default_cooling_technology
            else sku.form_factor.default_cooling_technology.first_cooling_time,
            "Охлаждение 2(для воды)": ""
            if not sku.form_factor.default_cooling_technology
            else sku.form_factor.default_cooling_technology.second_cooling_time,
            "Время посолки": ""
            if not sku.form_factor.default_cooling_technology
            else sku.form_factor.default_cooling_technology.salting_time,
            "Время налива": sku.made_from_boilings[0].boiling_technologies[0].pouring_time,
            "Время отвердевания": sku.made_from_boilings[0].boiling_technologies[0].soldification_time,
            "Время нарезки": sku.made_from_boilings[0].boiling_technologies[0].cutting_time,
            "Время слива": sku.made_from_boilings[0].boiling_technologies[0].pouring_off_time,
            "Дополнительное время": sku.made_from_boilings[0].boiling_technologies[0].extra_time,
            "Откачка": sku.made_from_boilings[0].boiling_technologies[0].pumping_out_time,
            "Kод": sku.code,
        }
        for sku in skus
    ]
    df = pd.DataFrame(data)
    filename = "mozzarella.xlsx"
    excel_path = os.path.join(
        os.path.dirname(flask.current_app.root_path), flask.current_app.config["UPLOAD_TMP_FOLDER"], filename
    )
    df.to_excel(excel_path)
    response = flask.send_from_directory(
        directory=os.path.join(
            os.path.dirname(flask.current_app.root_path),
            flask.current_app.config["UPLOAD_TMP_FOLDER"],
        ),
        path=filename,
        cache_timeout=0,
        as_attachment=True,
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response
