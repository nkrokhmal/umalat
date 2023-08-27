import os

from pathlib import Path

import flask
import flask_login
import pandas as pd

from app.globals import db
from app.main import main
from app.models.mascarpone import MascarponeBoiling, MascarponeBoilingTechnology, MascarponeSKU


def get_mascarpone_parameters() -> pd.DataFrame:
    skus: list[MascarponeSKU] = db.session.query(MascarponeSKU).all()
    data: list[dict[str, str | float | int]] = []

    for sku in skus:
        boiling: MascarponeBoiling = sku.made_from_boilings[0]
        boiling_technology: MascarponeBoilingTechnology = boiling.boiling_technologies[0]

        data.append(
            {
                "Название SKU": sku.name,
                "Процент": boiling.percent,
                "Наличие лактозы": "Да" if boiling.is_lactose else "Нет",
                "Вкусовая добавка": boiling.flavoring_agent,
                "Название форм фактора": sku.group.name,
                "Линия": "Маскарпоне",
                "Имя бренда": sku.brand_name,
                "Вес": sku.weight_netto,
                "Вес технология": boiling_technology.weight,
                "Коробки": sku.in_box,
                "Сепарация": boiling_technology.separation_time,
                "Анализ": boiling_technology.analysis_time,
                "Перекачка": boiling_technology.pumping_time,
                "Налив": boiling_technology.pouring_time,
                "Нагрев": boiling_technology.heating_time,
                "Посолка": boiling_technology.salting_time,
                "Ингридиенты": boiling_technology.ingredient_time,
                "Скорость фасовки": sku.packing_speed,
                "Выход": boiling.output_kg,
                "Коэффициент": boiling.output_coeff,
                "Константа": 0 if sku.group.name != "Сливки" else -100,
                "Kод": sku.code,
            }
        )
    return pd.DataFrame(data)


@main.route("/download_mascarpone", methods=["POST", "GET"])
@flask_login.login_required
def download_mascarpone() -> flask.Response:
    filename: str = "mascarpone.xlsx"
    root_path = Path(os.path.dirname(flask.current_app.root_path))
    excel_path = root_path / flask.current_app.config["UPLOAD_TMP_FOLDER"] / filename

    get_mascarpone_parameters().to_excel(excel_path)
    response = flask.send_from_directory(
        directory=root_path / flask.current_app.config["UPLOAD_TMP_FOLDER"],
        path=filename,
        as_attachment=True,
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


__all__ = [
    "download_mascarpone",
    "get_mascarpone_parameters",
]
