import os

import flask

from loguru import logger

from app.scheduler.adygea.properties.adygea_properties import AdygeaProperties
from app.scheduler.adygea.properties.parse_properties import parse_properties as parse_properties_adygea
from app.scheduler.butter.properties.butter_properties import ButterProperties
from app.scheduler.butter.properties.parse_properties import parse_properties as parse_properties_butter
from app.scheduler.mascarpone.properties.mascarpone_properties import MascarponeProperties
from app.scheduler.mascarpone.properties.parse_properties import parse_properties as parse_properties_mascarpone
from app.scheduler.mozzarella.properties.mozzarella_properties import MozzarellaProperties
from app.scheduler.mozzarella.properties.parse_properties import parse_properties as parse_properties_mozzarella
from app.scheduler.ricotta.properties.parse_properties import parse_properties as parse_properties_ricotta
from app.scheduler.ricotta.properties.ricotta_properties import RicottaProperties
from config import config


PROPERTY_CLASSES = {
    "mozzarella": MozzarellaProperties,
    "butter": ButterProperties,
    "adygea": AdygeaProperties,
    "ricotta": RicottaProperties,
    "mascarpone": MascarponeProperties,
}

EXCEL_PARSERS = {
    "mozzarella": parse_properties_mozzarella,
    "butter": parse_properties_butter,
    "adygea": parse_properties_adygea,
    "ricotta": parse_properties_ricotta,
    "mascarpone": parse_properties_mascarpone,
}


def load_properties_by_department(
    path: str,
    prefix: str,
):
    # NOTE: RETURNS BLANK PROPERTIES IF NOT PRESENT
    properties = {}

    for department in [
        "mozzarella",
        "butter",
        "adygea",
        "ricotta",
        "mascarpone",
    ]:
        # try to find in files

        filename = os.path.join(
            path,
            f"{prefix} Расписание {config.DEPARTMENT_ROOT_NAMES_BY_DEPARTMENT[department]}.xlsx",
        )

        if os.path.exists(filename):
            try:
                properties[department] = EXCEL_PARSERS[department](filename)
            except:
                raise Exception(
                    f"Произошла ошибка во время чтения параметров расписания из файла: {os.path.basename(filename)}"
                )
        else:
            properties[department] = PROPERTY_CLASSES[department]()
    return properties


def assert_properties_presence(properties, raise_if_not_present=None, warn_if_not_present=None):
    raise_if_not_present = raise_if_not_present or []
    warn_if_not_present = warn_if_not_present or []

    for department in raise_if_not_present:
        if not properties[department].is_present:
            raise Exception(
                f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES_BY_DEPARTMENT[department]}"
            )

    for department in warn_if_not_present:
        if not properties[department].is_present:
            logger.warning(
                f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES_BY_DEPARTMENT[department]}"
            )
            if os.environ.get("APP_ENVIRONMENT") == "runtime":
                flask.flash(
                    f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES_BY_DEPARTMENT[department]}",
                    "warning",
                )


def test():
    from pprint import pprint

    pprint(
        load_properties_by_department(
            path="/Users/marklidenberg/Documents/coding/repos/umalat/app/data/dynamic/2024-03-16/approved",
            prefix="2024-03-16",
        )
    )


if __name__ == "__main__":
    test()
