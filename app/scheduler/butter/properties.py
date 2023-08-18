import pydantic

from pydantic import Field

from app.scheduler.time import cast_human_time


class ButterProperties(pydantic.BaseModel):
    end_time: str = Field("", description="Конец работы маслоцеха")

    def is_present(self):
        if self.end_time:
            return True
        return False

    def department(self):
        return "butter"


def cast_properties(schedule=None):
    props = ButterProperties()
    if not schedule:
        return props
    props.end_time = cast_human_time(schedule.y[0])
    return props
