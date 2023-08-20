import os

import flask
import flask_login
import pandas as pd

from app.globals import db
from app.main import main
from app.models.butter import ButterSKU


@main.route("/download_butter", methods=["POST", "GET"])
@flask_login.login_required
def download_butter():
    skus = db.session.query(ButterSKU).all()
    data = [
        {
            "Название SKU": sku.name,
            "Процент": sku.made_from_boilings[0].percent,
            "Наличие лактозы": "Да" if sku.made_from_boilings[0].is_lactose else "Нет",
            "Вкусовая добавка": sku.made_from_boilings[0].flavoring_agent,
            "Название форм фактора": sku.group.name,
            "Линия": "Масло",
            "Имя бренда": sku.brand_name,
            "Вес нетто": sku.weight_netto,
            "Коробки": sku.in_box,
            "Вес форм фактора": 0,
            "Скорость упаковки": sku.packing_speed,
            "Разгон сепаратора": sku.made_from_boilings[0].boiling_technologies[0].separator_runaway_time,
            "Пастеризация": sku.made_from_boilings[0].boiling_technologies[0].pasteurization_time,
            "Набор": sku.made_from_boilings[0].boiling_technologies[0].increasing_temperature_time,
            "Kод": sku.code,
        }
        for sku in skus
    ]
    df = pd.DataFrame(data)
    filename = "butter.xlsx"
    excel_path = os.path.join(
        os.path.dirname(flask.current_app.root_path), flask.current_app.config["UPLOAD_TMP_FOLDER"], filename
    )
    df.to_excel(excel_path)
    response = flask.send_from_directory(
        directory=os.path.join(
            os.path.dirname(flask.current_app.root_path),
            flask.current_app.config["UPLOAD_TMP_FOLDER"],
        ),
        filename=filename,
        cache_timeout=0,
        as_attachment=True,
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response
