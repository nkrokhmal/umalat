# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *

from pydantic import Field

class ButterProperties(pydantic.BaseModel):
    end_time: str = Field('', description='Конец работы маслоцеха')
    def is_present(self):
        if self.end_time:
            return True
        return False


def parse_schedule(schedule):
    props = ButterProperties()
    props.end_time = cast_time(schedule.y[0])
    return props
