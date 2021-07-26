# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *


class RicottaProperties(pydantic.BaseModel):
    n_boilings: int = 0
    last_pumping_out_time: str = ''
    start_of_ninth_from_the_end_time: str = ''


def parse_schedule(schedule):
    props = RicottaProperties()
    ricotta_boilings = list(schedule.iter(cls='boiling'))
    with code('scotta input tanks'):
        props.n_boilings = len(ricotta_boilings)

    props.last_pumping_out_time = cast_time(ricotta_boilings[-1]['pumping_out'].y[0])
    if len(ricotta_boilings) < 9:
        props.start_of_ninth_from_the_end_time = cast_time(ricotta_boilings[-1].x[0])
    else:
        props.start_of_ninth_from_the_end_time = cast_time(ricotta_boilings[-9].x[0])

    return props
