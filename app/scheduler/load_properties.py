from app.imports.runtime import *
from app.scheduler.mozzarella.properties import (
    parse_schedule as parse_schedule_mozzarella,
)
from app.scheduler.ricotta.properties import parse_schedule as parse_schedule_ricotta
from app.scheduler.mascarpone.properties import (
    parse_schedule as parse_schedule_mascarpone,
)
from app.scheduler.milk_project.properties import (
    parse_schedule as parse_schedule_milk_project,
)
from app.scheduler.butter.properties import parse_schedule as parse_schedule_butter
from app.scheduler.adygea.properties import parse_schedule as parse_schedule_adygea

PARSERS = {
    "mozzarella": parse_schedule_mozzarella,
    "ricotta": parse_schedule_ricotta,
    "mascarpone": parse_schedule_mascarpone,
    "milk_project": parse_schedule_milk_project,
    "butter": parse_schedule_butter,
    "adygea": parse_schedule_adygea,
}


def load_properties(schedules):
    properties = {}
    for department in [
        "mozzarella",
        "ricotta",
        "milk_project",
        "butter",
        "mascarpone",
        "adygea",
    ]:
        if department in schedules and schedules[department] != "manual":
            properties[department] = PARSERS[department](schedules[department])
    return properties
