# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *


class MascarponeProperties(pydantic.BaseModel):
    fourth_boiling_group_adding_lactic_acid_time: str = ''
    last_pumping_off: str = ''

def parse_schedule(schedule):
    props = MascarponeProperties()

    boiling_groups = schedule['mascarpone_boiling_group', True]
    boiling_group = boiling_groups[-1] if len(boiling_groups) < 4 else boiling_groups[3]
    props.fourth_boiling_group_adding_lactic_acid_time = cast_time(boiling_group['boiling', True][-1]['boiling_process']['adding_lactic_acid'].y[0])

    boiling_groups = schedule['mascarpone_boiling_group', True]
    boiling_group = boiling_groups[-1]
    props.last_pumping_off = cast_time(boiling_group['boiling', True][-1]['boiling_process']['pumping_off'].y[0])

    return props
