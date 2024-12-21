import pydantic

from pydantic import Field


class ButterProperties(pydantic.BaseModel):
    is_present: bool = Field(False, description="Присутствует ли масло в этот день")

    end_time: str = Field("", description="Конец работы маслоцеха")

    separation_end_time: str = Field("", description="Конец работы сепарирования")

    def department(self):
        return "butter"
