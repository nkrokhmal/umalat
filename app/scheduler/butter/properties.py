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

    def department(self):
        return 'butter'

def cast_properties(schedule=None):
    props = ButterProperties()
    if not schedule:
        return props
    props.end_time = cast_time(schedule.y[0])
    return props
