from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.create_schedule_skeleton_block_maker import (
    create_schedule_skeleton_block_maker,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.fix_first_boiling_on_the_later_line import (
    fix_first_boiling_on_the_later_line,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_boilings.process_boilings import (
    process_boilings,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_cleanings import process_cleanings
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_extras import process_extras
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.process_shifts import process_shifts

from app.scheduler.shifts import *
from app.enum import LineName

from utils_ak.block_tree import *
from typing import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def make_schedule_from_boilings(
    boilings: List[ParallelepipedBlock],
    date: Optional[datetime] = None,
    cleanings: Optional[dict] = None,
    start_times: Optional[dict] = None,
    shrink_drenators: bool = True,
    start_configuration: Optional[list] = None,
) -> ParallelepipedBlock:

    # - Preprocess arguments

    start_configuration = start_configuration or [LineName.SALT]
    date = date or datetime.now()
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    start_times = {k: v if v else None for k, v in start_times.items()}
    cleanings = cleanings or {}  # {boiling_id: cleaning}

    # - Init block maker

    m = create_schedule_skeleton_block_maker(date=date)

    # - Process

    m = process_boilings(
        m=m,
        boilings=boilings,
        start_times=start_times,
        cleanings=cleanings,
        start_configuration=start_configuration,
        shrink_drenators=shrink_drenators,
    )
    m = process_extras(m=m)
    m = fix_first_boiling_on_the_later_line(m=m, start_configuration=start_configuration)
    m = process_cleanings(m=m)
    m = process_shifts(m=m)

    # - Return block

    return m.root
