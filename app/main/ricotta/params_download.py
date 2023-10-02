import os

from pathlib import Path

import flask
import flask_login
import pandas as pd

from app.globals import db
from app.main import main
from app.models.ricotta import RicottaBoiling, RicottaBoilingTechnology, RicottaSKU


@main.route("/download_ricotta", methods=["POST", "GET"])
@flask_login.login_required
def download_ricotta() -> flask.Response:
    skus: list[RicottaSKU] = db.session.query(RicottaSKU).all()
    data: list[dict] = []
    for sku in skus:
        boiling: RicottaBoiling = sku.made_from_boilings[0]
        technology: RicottaBoilingTechnology = boiling.boiling_technologies[0]

        data.append(
            {
                "Название SKU": sku.name,
                "Процент": boiling.percent,
                "Вкусовая добавка": boiling.flavoring_agent,
                "Название форм фактора": "Рикотта",
                "Линия": "Рикотта",
                "Имя бренда": sku.brand_name,
                "Вес нетто": sku.weight_netto,
                "Коробки": sku.in_box,
                "Вес форм фактора": 0,
                "Вход": boiling.input_kg,
                "Выход": boiling.output_kg,
                "Скорость упаковки": sku.packing_speed,
                "Набор сыворотки": technology.pouring_time,
                "Нагрев": technology.heating_time,
                "молочная кислота/выдерживание": technology.lactic_acid_time,
                "слив сыворотки": technology.drain_whey_time,
                "слив рикотты": technology.dray_ricotta_time,
                "посолка/анализ": technology.salting_time,
                "Перекачивание": technology.pumping_time,
                "Внесение ингредиентов": technology.ingredient_time,
                "Kод": sku.code,
            }
        )

    df = pd.DataFrame(data)
    filename = "ricotta.xlsx"
    path: Path = Path(os.path.dirname(flask.current_app.root_path)) / flask.current_app.config["UPLOAD_TMP_FOLDER"]
    df.to_excel(path / filename)
    response = flask.send_from_directory(
        directory=path,
        path=filename,
        as_attachment=True,
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response
