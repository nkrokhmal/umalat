# fmt: off
from typing import *

from pydantic import Field

from app.enum import *
from app.imports.runtime import *
from app.scheduler.time import *


class AdygeaProperties(pydantic.BaseModel):
    end_time: str = Field('', description='Конец работы адыгейского цеха')
    n_boilings: str = Field(0, description='Количество варок')

    def is_present(self):
        if self.end_time:
            return True
        return False

    def department(self):
        return 'adygea'

def cast_properties(schedule=None):
    props = AdygeaProperties()
    if not schedule:
        return props
    props.end_time = cast_human_time(schedule.y[0])
    props.n_boilings = len(schedule['boiling', True])
    return props
