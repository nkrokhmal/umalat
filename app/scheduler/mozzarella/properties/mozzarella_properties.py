from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *

from pydantic import Field


class MozzarellaProperties(pydantic.BaseModel):
    bar12_present: bool = Field(False, description="Присутствует ли брус 1.2")
    line33_last_termizator_end_times: str = Field(
        [], description="Времена заполнения танков на смеси 3.3% (каждая 9 варка)"
    )
    line36_last_termizator_end_times: str = Field(
        [], description="Времена заполнения танков на смеси 3.6% (каждая 9 варка)"
    )
    line27_last_termizator_end_times: str = Field(
        [], description="Времена заполнения танков на смеси 2.7% (каждая 9 варка)"
    )

    def termizator_times(self):
        res = {
            "2.7": self.line27_last_termizator_end_times,
            "3.3": self.line33_last_termizator_end_times,
            "3.6": self.line36_last_termizator_end_times,
        }
        # todo later: maybe, make proper checks, maybe make some warnings or something [@marklidenberg]
        # assert len(sum(res.values(), [])) <= 4, 'Указано больше 4 танков смесей. В производстве есть только 4 танка смесей. '
        return res

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

    water_melting_end_time: str = Field("", description="Конец работы линии воды")
    salt_melting_end_time: str = Field("", description="Конец работы линии соли")

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

    def is_present(self):
        if self.water_melting_end_time or self.salt_melting_end_time:
            return True
        return False

    def department(self):
        return "mozzarella"
