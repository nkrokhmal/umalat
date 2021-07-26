# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *


class ButterProperties(pydantic.BaseModel):
    end_time: str = ''


def parse_schedule(schedule):
    props = ButterProperties()
    props.end_time = cast_time(schedule.y[0])
    return props
