from typing import List

import pydantic

from pydantic import Field


class MozzarellaProperties(pydantic.BaseModel):
    is_present: bool = Field(False, description="Присутствует ли моцарелла в этот день")
    bar12_present: bool = Field(False, description="Присутствует ли брус 1.2")

    every_8th_pouring_end_27: list[str] = Field([], description="Времена окончания каждого 8-й налива на 2.7")
    every_8th_pouring_end_32: list[str] = Field([], description="Времена окончания каждого 8-й налива на 3.2")

    multihead_end_time: str = Field("", description="Конец работы мультиголовы (пусто, если мультиголова не работает)")
    water_multihead_present: bool = Field(False, description="Есть ли мультиголова на воде в этот день")

    short_cleaning_times: List[str] = Field([], description="Короткие мойки")
    full_cleaning_times: List[str] = Field([], description="Полные мойки")

    salt_melting_start_time: str = Field("", description="Начало плавления на линии соли")

    cheesemaker1_end_time: str = Field("", description="Конец работы 1 сыроизготовителя")
    cheesemaker2_end_time: str = Field("", description="Конец работы 2 сыроизготовителя")
    cheesemaker3_end_time: str = Field("", description="Конец работы 3 сыроизготовителя")
    cheesemaker4_end_time: str = Field("", description="Конец работы 4 сыроизготовителя")

    def cheesemaker_times(self):
        values = [[i, getattr(self, f"cheesemaker{i}_end_time")] for i in range(1, 5)]
        values = [value for value in values if value[1]]
        return values

    water_packing_end_time: str = Field("", description="Конец работы паковки воды")
    salt_packing_end_time: str = Field("", description="Конец работы паковки соли")
    water_melting_end_time: str = Field("", description="Конец работы плавления воды")
    salt_melting_end_time: str = Field("", description="Конец работы плавления соли")

    drenator1_end_time: str = Field("", description="Конец работы 1 дренатора")
    drenator2_end_time: str = Field("", description="Конец работы 2 дренатора")
    drenator3_end_time: str = Field("", description="Конец работы 3 дренатора")
    drenator4_end_time: str = Field("", description="Конец работы 4 дренатора")
    drenator5_end_time: str = Field("", description="Конец работы 5 дренатора")
    drenator6_end_time: str = Field("", description="Конец работы 6 дренатора")
    drenator7_end_time: str = Field("", description="Конец работы 7 дренатора")
    drenator8_end_time: str = Field("", description="Конец работы 8 дренатора")

    def drenator_times(self):
        values = [[i, getattr(self, f"drenator{i}_end_time")] for i in range(1, 9)]
        values = [value for value in values if value[1]]
        return values

    def department(self):
        return "mozzarella"

    @property
    def every_8th_pouring_end(self):
        return {"2.7": self.every_8th_pouring_end_27, "3.2": self.every_8th_pouring_end_32}
