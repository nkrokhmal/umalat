# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *

from pydantic import Field

class AdygeaProperties(pydantic.BaseModel):
    end_time: str = Field('', description='Конец работы адыгейского цеха')


def parse_schedule(schedule):
    props = AdygeaProperties()
    props.end_time = cast_time(schedule.y[0])
    return props
