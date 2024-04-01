import pydantic

from pydantic import Field

from app.scheduler.time_utils import cast_human_time


class MascarponeProperties(pydantic.BaseModel):
    end_time: str = Field("", description="Конец работы маслоцеха")
    every_8t_of_separation: list = Field([], description="Каждые 8 тонн сепарации")

    def is_present(self):
        return bool(self.end_time)

    def department(self):
        return "mascarpone"


def cast_properties(schedule=None):
    props = MascarponeProperties()
    if not schedule:
        return props
    props.end_time = cast_human_time(schedule.y[0])
    return props
