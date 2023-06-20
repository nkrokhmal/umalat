from app.imports.runtime import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.make_termizator_cleaning_block import (
    make_termizator_cleaning_block,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.validator import Validator

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.scheduler.shifts import *
from app.enum import LineName

from app.scheduler.mozzarella.algo.schedule.custom_pushers import *
from utils_ak.block_tree import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


class ScheduleMaker:

    def make(
        self, boilings, date=None, cleanings=None, start_times=None, start_configuration=None, shrink_drenators=True
    ):

        self._process_extras()
        self._fix_first_boiling_of_later_line(start_configuration)
        self._process_cleanings()
        self._process_shifts()
        return self.m.root
