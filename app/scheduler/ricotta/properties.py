# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *

from pydantic import Field

class RicottaProperties(pydantic.BaseModel):
    n_boilings: int = Field(0, description='Число варок (используется для расчета скотты)')
    last_pumping_out_time: str = Field('', description='Конец последнего слива')
    start_of_ninth_from_the_end_time: str = Field('', description='Начало девятой варки с конца')


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
