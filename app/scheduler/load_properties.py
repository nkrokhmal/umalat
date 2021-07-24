from app.imports.runtime import *
from app.scheduler.mozzarella.properties import (
    parse_schedule as parse_schedule_mozzarella,
)
from app.scheduler.ricotta.properties import parse_schedule as parse_schedule_ricotta
from app.scheduler.mascarpone.properties import (
    parse_schedule as parse_schedule_mascarpone,
)


def load_properties(schedules):
    properties = {}
    properties["mozzarella"] = parse_schedule_mozzarella(schedules["mozzarella"])
    properties["ricotta"] = parse_schedule_mozzarella(schedules["ricotta"])

    if "mascarpone" in schedules:
        properties["mascarpone"] - parse_schedule_mascarpone(schedules["mascarpone"])
