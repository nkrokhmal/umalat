from app.imports.runtime import *
from app.scheduler.mozzarella.properties import (
    parse_schedule as parse_schedule_mozzarella,
)


def load_properties(schedules):
    return {"mozzarella": parse_schedule_mozzarella(schedules["mozzarella"])}
