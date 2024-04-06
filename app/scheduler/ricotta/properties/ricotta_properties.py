import pydantic

from pydantic import Field

from app.scheduler.time_utils import cast_human_time


class RicottaProperties(pydantic.BaseModel):
    is_present: bool = Field(False, description="Присутствует ли рикотта в этот день")

    last_pumping_out_time: str = Field("", description="Конец последнего слива")
    every_5th_pouring_times: list[str] = Field("", description="Каждый 5-й набор")
    last_pouring_time: str = Field("", description="Конец последнего набора")

    def is_present(self):
        if self.last_pumping_out_time:
            return True
        return False

    def department(self):
        return "ricotta"


def cast_properties(schedule=None):
    props = RicottaProperties()
    if not schedule:
        return props
    ricotta_boilings = list(schedule.iter(cls="boiling"))

    props.n_boilings = len(ricotta_boilings)

    props.last_pumping_out_time = cast_human_time(ricotta_boilings[-1]["pumping_out"].y[0])

    return props
