from app.imports.runtime import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.create_left_df import create_left_df
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.create_lines_df import create_lines_df
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.create_multihead_water_boilings import (
    create_multihead_water_boilings,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.create_schedule_skeleton_block_maker import (
    create_schedule_skeleton_block_maker,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.fix_first_boiling_on_the_later_line import (
    fix_first_boiling_on_the_later_line,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_boilings import process_boilings
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_cleanings import process_cleanings
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_extras import process_extras
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_shifts import process_shifts
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.schedule_maker import ScheduleMaker

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.scheduler.shifts import *
from app.enum import LineName

from app.scheduler.mozzarella.algo.schedule.custom_pushers import *
from utils_ak.block_tree import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def make_schedule_from_boilings(
    boilings,
    date=None,
    cleanings=None,
    start_times=None,
    shrink_drenators=True,
    start_configuration=None,
) -> ParallelepipedBlock:

    # - Preprocess arguments

    start_configuration = start_configuration or [LineName.SALT]
    date = date or datetime.now()
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    start_times = {k: v if v else None for k, v in start_times.items()}
    cleanings = cleanings or {}  # {boiling_id: cleaning}

    # - Prepare collaterel variables

    lines_df = create_lines_df(start_times=start_times)
    left_df = create_left_df(boilings=boilings)
    multihead_water_boilings, last_multihead_water_boiling = create_multihead_water_boilings(left_df=left_df)

    # - Init block maker

    m = create_schedule_skeleton_block_maker(date=date)

    m = process_boilings(
        m=m,
        left_df=left_df,
        last_multihead_water_boiling=last_multihead_water_boiling,
        lines_df=lines_df,
        cleanings=cleanings,
        start_configuration=start_configuration,
        shrink_drenators=shrink_drenators,
    )
    m = process_extras(m=m)
    m = fix_first_boiling_on_the_later_line(m=m, start_configuration=start_configuration)
    m = process_cleanings(m=m)
    m = process_shifts(m=m)
    return m.root
