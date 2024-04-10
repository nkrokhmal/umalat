import pydantic

from pydantic import Field

from app.scheduler.time_utils import cast_human_time


class MascarponeProperties(pydantic.BaseModel):
    is_present: bool = Field(False, description="Присутствует ли маскарпоне в этот день")

    end_time: str = Field("", description="Конец работы маслоцеха")
    every_8t_of_separation: list = Field([], description="Каждые 8 тонн сепарации")

    def department(self):
        return "mascarpone"


def test():
    print(MascarponeProperties())


if __name__ == "__main__":
    test()
