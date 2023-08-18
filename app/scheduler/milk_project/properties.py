import pydantic

from pydantic import Field

from app.scheduler.milk_project.properties import MilkProjectProperties
from app.scheduler.time import cast_human_time


class MilkProjectProperties(pydantic.BaseModel):
    end_time: str = Field("", description="Конец работы милк-проджекта")
    n_boilings: str = Field(0, description="Количество варок")

    def is_present(self):
        if self.end_time:
            return True
        return False

    def department(self):
        return "milk_project"


def cast_properties(schedule=None):
    props = MilkProjectProperties()
    if not schedule:
        return props
    props.end_time = cast_human_time(schedule.y[0])
    props.n_boilings = len(schedule["boiling_sequence", True])
    return props
