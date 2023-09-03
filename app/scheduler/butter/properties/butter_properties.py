import pydantic

from pydantic import Field


class ButterProperties(pydantic.BaseModel):
    end_time: str = Field("", description="Конец работы маслоцеха")

    def is_present(self):
        return bool(self.end_time)

    def department(self):
        return "butter"


def test():
    pass
