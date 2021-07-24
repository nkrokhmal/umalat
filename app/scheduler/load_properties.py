from app.imports.runtime import *
from app.scheduler.mozzarella.properties import (
    parse_schedule as parse_schedule_mozzarella,
)
from app.scheduler.ricotta.properties import parse_schedule as parse_schedule_ricotta


def load_properties(schedules):
    return {
        "mozzarella": parse_schedule_mozzarella(schedules["mozzarella"]),
        "ricotta": parse_schedule_ricotta(schedules["ricotta"]),
    }
