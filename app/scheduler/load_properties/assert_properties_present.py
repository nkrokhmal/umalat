from app.imports.runtime import *

def assert_properties_presence(
    properties, raise_if_not_present=None, warn_if_not_present=None
):
    raise_if_not_present = raise_if_not_present or []
    warn_if_not_present = warn_if_not_present or []

    for department in raise_if_not_present:
        if not properties[department].is_present():
            raise Exception(
                f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}"
            )

    for department in warn_if_not_present:
        if not properties[department].is_present():
            logger.warning(
                f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}"
            )
            if os.environ.get("APP_ENVIRONMENT") == "runtime":
                flask.flash(
                    f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}",
                    "warning",
                )

