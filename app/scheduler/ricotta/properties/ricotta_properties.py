import pydantic

from pydantic import Field


class RicottaProperties(pydantic.BaseModel):
    is_present: bool = Field(False, description="Присутствует ли рикотта в этот день")

    last_pumping_out_time: str = Field("", description="Конец последнего слива")
    every_5th_pouring_times: list[str] = Field([], description="Каждый 5-й набор")
    last_pouring_time: str = Field("", description="Конец последнего набора")

    def department(self):
        return "ricotta"
