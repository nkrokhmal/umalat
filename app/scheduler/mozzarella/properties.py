# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *

from pydantic import Field


class MozzarellaProperties(pydantic.BaseModel):
    bar12_present: bool = Field(False, description='Присутствует ли брус 1.2')
    line33_last_termizator_end_times: str = Field([], description='Времена заполнения танков на смеси 3.3% (каждая 9 варка)')
    line36_last_termizator_end_times: str = Field([], description='Времена заполнения танков на смеси 3.6% (каждая 9 варка)')
    line27_last_termizator_end_times: str = Field([], description='Времена заполнения танков на смеси 2.7% (каждая 9 варка)')

    def termizator_times(self):
        res = {'2.7': self.line27_last_termizator_end_times,
                '3.3': self.line33_last_termizator_end_times,
                '3.6': self.line36_last_termizator_end_times}
        assert len(sum(res.values(), [])) <= 4, 'Указано больше 4 танков смесей. В производстве есть только 4 танка смесей. '
        return res
    
    multihead_end_time: str = Field("", description='Конец работы мультиголовы (пусто, если мультиголова не работает)')
    water_multihead_present: bool = Field(False, description='Конец работы мультиголовы на воде (пусто, если мультиголова на воде не работает)')

    short_cleaning_times: List[str] = Field([], description='Короткие мойки')
    full_cleaning_times: List[str] = Field([], description='Полные мойки')

    salt_melting_start_time: str = Field('', description='Начало плавления на линии соли')

    cheesemaker1_end_time: str = Field('', description='Конец работы 1 сыроизготовителя')
    cheesemaker2_end_time: str = Field('', description='Конец работы 2 сыроизготовителя')
    cheesemaker3_end_time: str = Field('', description='Конец работы 3 сыроизготовителя')
    cheesemaker4_end_time: str = Field('', description='Конец работы 4 сыроизготовителя')

    def cheesemaker_times(self):
        values = [[i, getattr(self, f'cheesemaker{i}_end_time')] for i in range(1, 5)]
        values = [value for value in values if value[1]]
        return values

    water_melting_end_time: str = Field('', description='Конец работы линии воды')
    salt_melting_end_time: str = Field('', description='Конец работы линии соли')

    drenator1_end_time: str = Field('', description='Конец работы 1 дренатора')
    drenator2_end_time: str = Field('', description='Конец работы 2 дренатора')
    drenator3_end_time: str = Field('', description='Конец работы 3 дренатора')
    drenator4_end_time: str = Field('', description='Конец работы 4 дренатора')
    drenator5_end_time: str = Field('', description='Конец работы 5 дренатора')
    drenator6_end_time: str = Field('', description='Конец работы 6 дренатора')
    drenator7_end_time: str = Field('', description='Конец работы 7 дренатора')
    drenator8_end_time: str = Field('', description='Конец работы 8 дренатора')

    def drenator_times(self):
        values = [[i, getattr(self, f'drenator{i}_end_time')] for i in range(1, 9)]
        values = [value for value in values if value[1]]
        return values

    def is_present(self):
        if self.water_melting_end_time or self.salt_melting_end_time:
            return True
        return False

    def department(self):
        return 'mozzarella'

def cast_properties(schedule=None):
    props = MozzarellaProperties()
    if not schedule:
        return props

    with code("bar12_present"):
        skus = sum(
            [
                list(b.props["boiling_group_df"]["sku"])
                for b in schedule["master"]["boiling", True]
            ],
            [],
        )
        props.bar12_present = "1.2" in [sku.form_factor.name for sku in skus]

    with code('2.7, 3.3, 3.6 tanks'):
        boilings = schedule['master']['boiling', True]

        _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == '3.3']
        if _boilings:
            _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
            props.line33_last_termizator_end_times = [cast_time(b['pouring']['first']['termizator'].y[0]) for b in _tank_boilings]

        _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == '3.6']
        if _boilings:
            _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
            props.line36_last_termizator_end_times = [cast_time(b['pouring']['first']['termizator'].y[0]) for b in _tank_boilings]

        _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == '2.7']
        if _boilings:
            _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
            props.line27_last_termizator_end_times = [cast_time(b['pouring']['first']['termizator'].y[0]) for b in _tank_boilings]

    with code('multihead'):
        multihead_packings = list(schedule.iter(cls='packing', boiling_group_df=lambda df: df['sku'].iloc[0].packers[0].name == 'Мультиголова'))
        if multihead_packings:
            props.multihead_end_time = cast_time(max(packing.y[0] for packing in multihead_packings))

        water_multihead_packings = list(schedule.iter(cls='packing', boiling_group_df=lambda df: df['sku'].iloc[0].packers[0].name == 'Мультиголова' and df.iloc[0]['boiling'].line.name == LineName.WATER))
        if water_multihead_packings:
            props.water_multihead_present = True

    with code('cleanings'):
        props.short_cleaning_times = [cast_time(cleaning.x[0]) for cleaning in schedule['master']['cleaning', True] if cleaning.props['cleaning_type'] == 'short']
        props.full_cleaning_times = [cast_time(cleaning.x[0]) for cleaning in schedule['master']['cleaning', True] if cleaning.props['cleaning_type'] == 'full']

    with code('meltings'):
        salt_boilings = [b for b in schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']
        if salt_boilings:
            props.salt_melting_start_time = cast_time(salt_boilings[0]['melting_and_packing']['melting']['meltings'].x[0])

    with code('cheesemakers'):
        values = []
        for b in schedule['master']['boiling', True]:
            values.append([b.props['pouring_line'], b['pouring'].y[0]])
        df = pd.DataFrame(values, columns=['pouring_line', 'finish'])
        values = df.groupby('pouring_line').agg(max).to_dict()['finish']
        values = list(sorted(values.items(), key=lambda kv: kv[0]))  # [('0', 116), ('1', 97), ('2', 149), ('3', 160)]
        values_dict = dict(values)
        props.cheesemaker1_end_time = cast_time(values_dict.get('0'))
        props.cheesemaker2_end_time = cast_time(values_dict.get('1'))
        props.cheesemaker3_end_time = cast_time(values_dict.get('2'))
        props.cheesemaker4_end_time = cast_time(values_dict.get('3'))

    with code('melting end'):
        lines_df = pd.DataFrame(index=['water', 'salt'])
        lines_df['boilings'] = None
        lines_df.loc['water', 'boilings'] = [b for b in schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Моцарелла в воде']
        lines_df.loc['salt', 'boilings'] = [b for b in schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']
        lines_df['melting_end'] = lines_df['boilings'].apply(lambda boilings: None if not boilings else boilings[-1]['melting_and_packing']['melting'].y[0])
        props.water_melting_end_time = cast_time(lines_df.loc['water', 'melting_end'])
        props.salt_melting_end_time = cast_time(lines_df.loc['salt', 'melting_end'])

    with code('drenators'):
        # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
        values = []
        for boiling in schedule['master']['boiling', True]:
            drenator = boiling['drenator']
            values.append([drenator.y[0], drenator.props['pouring_line'], drenator.props['drenator_num']])
        df = pd.DataFrame(values, columns=['drenator_end', 'pouring_line', 'drenator_num'])
        df['id'] = df['pouring_line'].astype(int) * 2 + df['drenator_num'].astype(int)
        df = df[['id', 'drenator_end']]
        df = df.drop_duplicates(subset='id', keep='last')
        df = df.reset_index(drop=True)
        df['id'] = df['id'].astype(int) + 1

        df = df.sort_values(by='id')

        values = df.values.tolist()
        values_dict = dict(values)
        props.drenator1_end_time = cast_time(values_dict.get(1))
        props.drenator2_end_time = cast_time(values_dict.get(2))
        props.drenator3_end_time = cast_time(values_dict.get(3))
        props.drenator4_end_time = cast_time(values_dict.get(4))
        props.drenator5_end_time = cast_time(values_dict.get(5))
        props.drenator6_end_time = cast_time(values_dict.get(6))
        props.drenator7_end_time = cast_time(values_dict.get(7))
        props.drenator8_end_time = cast_time(values_dict.get(8))

    return props
