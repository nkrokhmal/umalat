from app.imports.runtime import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.schedule_maker import ScheduleMaker

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.scheduler.shifts import *
from app.enum import LineName

from app.scheduler.mozzarella.algo.schedule.custom_pushers import *
from utils_ak.block_tree import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def make_schedule_from_boilings(
    boilings, date=None, cleanings=None, start_times=None, shrink_drenators=True, start_configuration=None
):
    return ScheduleMaker().make(
        boilings,
        date,
        cleanings,
        start_times,
        shrink_drenators=shrink_drenators,
        start_configuration=start_configuration,
    )
