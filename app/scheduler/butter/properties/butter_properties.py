import pydantic

from pydantic import Field

from app.scheduler.time_utils import cast_human_time


class ButterProperties(pydantic.BaseModel):
    end_time: str = Field("", description="Конец работы маслоцеха")

    def is_present(self):
        return bool(self.end_time)

    def department(self):
        return "butter"


def cast_butter_properties(schedule=None):
    props = ButterProperties()
    if not schedule:
        return props
    props.end_time = cast_human_time(schedule.y[0])
    return props
