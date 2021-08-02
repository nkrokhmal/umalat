# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *
from typing import *
from app.enum import *

from pydantic import Field


class MozzarellaProperties(pydantic.BaseModel):
    bar12_present: bool = Field(False, description='Был ли вчера брус 1.2')
    line33_last_termizator_end_time: str = Field("", description='Конец последнего налива термизатора на смеси 3.3%')
    line36_last_termizator_end_time: str = Field("", description='Конец последнего налива термизатора на смеси 3.6%')
    line27_nine_termizator_end_time: str = Field("", description='Конец девятого налива термизатора на смеси 2.7%')
    line27_last_termizator_end_time: str = Field("", description='Конец последнего налива термизатора на смеси 2.7%')

    def termizator_times(self):
        return {'2.7': {'last': self.line27_last_termizator_end_time, 'ninth': self.line27_nine_termizator_end_time},
                '3.3': {'last': self.line33_last_termizator_end_time},
                '3.6': {'last': self.line36_last_termizator_end_time}}

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


def parse_schedule(schedule):
    props = MozzarellaProperties()

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
            props.line33_last_termizator_end_time = cast_time(_boilings[-1]['pouring']['first']['termizator'].y[0])
            assert len(_boilings) <= 9, 'Слишком много наливов на смеси 3.3'

        _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == '3.6']
        if _boilings:
            props.line36_last_termizator_end_time = cast_time(_boilings[-1]['pouring']['first']['termizator'].y[0])
            assert len(_boilings) <= 9, 'Слишком много наливов на смеси 3.6'

        _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == '2.7']
        if _boilings:
            assert len(_boilings) <= 18, 'Слишком много наливов на смеси 2.7'

            if len(_boilings) >= 10:
                props.line27_nine_termizator_end_time = cast_time(_boilings[8]['pouring']['first']['termizator'].y[0])
            props.line27_last_termizator_end_time = cast_time(_boilings[-1]['pouring']['first']['termizator'].y[0])

    with code('multihead'):
        multihead_packings = list(schedule.iter(cls='packing', boiling_group_df=lambda df: df['sku'].iloc[0].packers[0].name == 'Мультиголова'))
        if multihead_packings:
            props.multihead_end_time = max(packing.y[0] for packing in multihead_packings)

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
