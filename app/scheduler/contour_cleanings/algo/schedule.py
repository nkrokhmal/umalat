# fmt: off
from app.imports.runtime import *
from utils_ak.block_tree import *
from app.scheduler.time import *
from app.enum import *

def calc_scotta_input_tanks(schedules):
    scotta_per_boiling = 1900 - 130
    values = [['4', 80000], ['5', 80000], ['8', 80000]]
    tanks_df = pd.DataFrame(values, columns=['id', 'kg'])
    tanks_df['max_boilings'] = tanks_df['kg'].apply(
        lambda kg: int(custom_round(kg / scotta_per_boiling, 1, rounding='floor')))
    tanks_df['n_boilings'] = None
    tanks_df['scotta'] = None

    boilings = list(schedules['ricotta'].iter(cls='boiling'))
    total_scotta = len(boilings) * scotta_per_boiling

    left_scotta = total_scotta

    assert len(boilings) <= tanks_df[
        'max_boilings'].sum(), 'Слишком много варок на линии рикотты. Скотта не помещается в танки.'
    for i, row in tanks_df.iterrows():
        if not left_scotta:
            break

        max_scotta = row['max_boilings'] * scotta_per_boiling
        cur_scotta = min(max_scotta, left_scotta)
        left_scotta -= cur_scotta

        tanks_df.loc[i, 'scotta'] = cur_scotta

    tanks_df = tanks_df.fillna(0)
    tanks_df['scotta'] /= 1000.
    return tanks_df[['id', 'scotta']].values.tolist()


class CleaningValidator(ClassValidator):
    def __init__(self, window=30, ordered=True):
        self.ordered = ordered
        super().__init__(window=window)

    def validate__cleaning__cleaning(self, b1, b2):
        validate_disjoint_by_axis(b1, b2, distance=2, ordered=self.ordered)


def run_order(function_or_generators, order):
    for i in order:
        obj = function_or_generators[i]
        if callable(obj):
            obj()
        elif isinstance(obj, types.GeneratorType):
            next(obj)


def _make_contour_1(schedules, order=(0, 1, 2), milk_project_end_time=None, adygea_end_time=None):
    milk_project_end_time = _init_end_time(schedules, 'milk_project', milk_project_end_time)
    adygea_end_time = _init_end_time(schedules, 'adygea', adygea_end_time)

    m = BlockMaker("1 contour")
    m.row('cleaning', push_func=add_push,
          size=cast_t('01:20'), x=cast_t('06:30'),
          label='Линиия отгрузки')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия приемки молока 1 + проверить фильтр')

    with code('Tanks'):
        boilings = schedules['mozzarella']['master']['boiling', True]

        # get values when different percentage tanks end: [['3.6', 74], ['3.3', 94], ['2.7', 144]]
        values = []
        for percent in ['2.7', '3.3', '3.6']:
            _boilings = [b for b in boilings if str(b.props['boiling_model'].percent) == percent]

            if percent == '2.7':
                assert len(_boilings) <= 18, f'Слишком много наливов на смеси {percent}'
            else:
                assert len(_boilings) <= 9, f'Слишком много наливов на смеси {percent}'

            if len(_boilings) >= 10:
                values.append([percent, _boilings[8]['pouring']['first']['termizator'].y[0], '01:50', False])

            if len(_boilings) > 0:
                values.append([percent, _boilings[-1]['pouring']['first']['termizator'].y[0], '01:50', False])
            else:
                # no boilings found today
                values.append([percent, cast_t('10:00'), '01:05', True])

        df = pd.DataFrame(values, columns=['percent', 'pouring_end', 'time', 'is_short'])
        df = df[['percent', 'pouring_end', 'time', 'is_short']]
        df = df.sort_values(by='pouring_end')
        values = df.values.tolist()

        for percent, end, time, is_short in values:
            label = f'Танк смесей {percent}' if not is_short else f'Танк смесей {percent} (кор. мойка)'
            m.row('cleaning', push_func=AxisPusher(start_from=end, validator=CleaningValidator(ordered=False)),
                  size=cast_t(time),
                  label=label)

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия отгрузки')

    def f1():
        if 'adygea' in schedules:
            m.row('cleaning', push_func=AxisPusher(start_from=adygea_end_time, validator=CleaningValidator()),
                  size=cast_t('01:50'),
                  label='Линия адыгейского')

    def f2():
        if 'milk_project' in schedules:
            m.row('cleaning',
                  push_func=AxisPusher(start_from=[milk_project_end_time, adygea_end_time], validator=CleaningValidator()),
                  size=cast_t('02:20'),
                  label='Милкпроджект')

    def f3():
        if 'milk_project' in schedules:
            m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
                  size=cast_t('01:20'),
                  label='Танк роникс')

    run_order([f1, f2, f3], order)

    for _ in range(3):
        m.row('cleaning', push_func=AxisPusher(start_from=0, validator=CleaningValidator(ordered=False)),
              size=cast_t('01:50'),
              label='Танк сырого молока')

    for _ in range(2):
        m.row('cleaning', push_func=AxisPusher(start_from=0, validator=CleaningValidator(ordered=False)),
              size=cast_t('01:50'),
              label='Танк обрата')

    return m.root


def make_contour_1(schedules, milk_project_end_time=None, adygea_end_time=None):
    df = utils.optimize(_make_contour_1, lambda b: -b.y[0], schedules, milk_project_end_time=milk_project_end_time, adygea_end_time=adygea_end_time)
    return df.iloc[-1]['output']


def make_contour_2(schedules):
    m = BlockMaker("2 contour")
    m.row('cleaning', push_func=add_push,
          size=cast_t('01:20'), x=cast_t('12:00'),
          label='Линия обрата в сливки')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Сливки от пастера 25')

    with code('Мультиголова'):
        multihead_packings = list(schedules['mozzarella'].iter(cls='packing', boiling_group_df=lambda df: df['sku'].iloc[0].packers[0].name == 'Мультиголова'))
        if multihead_packings:
            multihead_end = max(packing.y[0] for packing in multihead_packings) + 12 # add hour for preparation
            m.row('cleaning', push_func=AxisPusher(start_from=['last_end', multihead_end], validator=CleaningValidator()),
                  size=cast_t('01:20'),
                  label='Комет')

        water_multihead_packings = list(schedules['mozzarella'].iter(cls='packing', boiling_group_df=lambda df: df['sku'].iloc[0].packers[0].name == 'Мультиголова' and df.iloc[0]['boiling'].line.name == LineName.WATER))
        if water_multihead_packings:
            m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
                  size=cast_t('01:20'),
                  label='Фасовочная вода')

    m.row('cleaning', push_func=AxisPusher(start_from=cast_t('1:04:00'), validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Танк ЖВиКС 1')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Танк ЖВиКС 2')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Жирная вода на сепаратор')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Сливки от сепаратора жирной воды')

    return m.root


def _make_contour_3(schedules, order1=(0, 1, 1, 1, 1), order2=(0, 0, 0, 0, 0, 1)):
    m = BlockMaker("3 contour")

    for cleaning in schedules['mozzarella']['master']['cleaning', True]:
        label = 'Короткая мойка термизатора' if cleaning.props['cleaning_type'] == 'short' else 'Полная мойка термизатора'
        m.row('cleaning', push_func=add_push,
              size=cleaning.size[0],
              x=cleaning.x[0],
              label=label)

    def f1():
        salt_boilings = [b for b in schedules['mozzarella']['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']
        if salt_boilings:
            salt_melting_start = salt_boilings[0]['melting_and_packing']['melting']['meltings'].x[0]
            m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator(ordered=False), start_from=salt_melting_start + 6),
                  size=90 // 5,
                  label='Контур циркуляции рассола')

    def g2():
        with code('cheese_makers'):
            # get when cheese makers end (values -> [('1', 97), ('0', 116), ('2', 149), ('3', 160)])
            values = []
            for b in schedules['mozzarella']['master']['boiling', True]:
                values.append([b.props['pouring_line'], b['pouring'].y[0]])
            df = pd.DataFrame(values, columns=['pouring_line', 'finish'])
            values = df.groupby('pouring_line').agg(max).to_dict()['finish']
            values = list(sorted(values.items(), key=lambda kv: kv[1])) # [('1', 97), ('0', 116), ('2', 149), ('3', 160)]

            for n, cheese_maker_end in values:
                m.row('cleaning', push_func=AxisPusher(start_from=cheese_maker_end, validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:20'),
                      label=f'Сыроизготовитель {int(n) + 1}')
                yield

        with code('non-used cheesemakers'):
            non_used_ids = set([str(x) for x in range(4)]) - set(df['pouring_line'].unique())
            for id in non_used_ids:
                m.row('cleaning', push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:05'),
                      label=f'Сыроизготовитель {int(id) + 1} (кор. мойка)')
                yield


    run_order([f1, g2()], order1)

    def g3():
        with code('melters_and_baths'):
            lines_df = pd.DataFrame(index=['water', 'salt'])
            lines_df['boilings'] = None

            lines_df.loc['water', 'boilings'] = [b for b in schedules['mozzarella']['master']['boiling', True] if b.props['boiling_model'].line.name == 'Моцарелла в воде']
            lines_df.loc['salt', 'boilings'] = [b for b in schedules['mozzarella']['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']

            lines_df['cleanings'] = [[] for _ in range(2)]
            if lines_df.loc['water', 'boilings']:
                lines_df.loc['water', 'cleanings'].extend([m.create_block('cleaning',
                                                                          size=(cast_t('02:20'), 0),
                                                                          label='Линия 1 плавилка'),
                                                           m.create_block('cleaning',
                                                                          size=(cast_t('01:30'), 0),
                                                                          label='Линия 1 ванна 1 + ванна 2')])
            else:
                # no water used
                m.row('cleaning', push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:45'),
                      label=f'Линия 1 плавилка (кор. мойка)')
                m.row('cleaning', push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:15'),
                      label=f'Линия 1 ванна 1 + ванна 2 (кор. мойка)')

            if lines_df.loc['salt', 'boilings']:
                lines_df.loc['salt', 'cleanings'].extend([m.create_block('cleaning',
                                                                         size=(cast_t('02:20'), 0),
                                                                         label='Линия 2 плавилка'),
                                                          m.create_block('cleaning',
                                                                         size=(cast_t('01:30'), 0),
                                                                         label='Линия 2 ванна 1'),
                                                          m.create_block('cleaning',
                                                                         size=(cast_t('01:30'), 0),
                                                                         label='Линия 2 ванна 2')])
            else:
                # no salt used
                m.row('cleaning',
                      push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:45'),
                      label=f'Линия 2 плавилка (кор. мойка)')
                m.row('cleaning',
                      push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:15'),
                      label=f'Линия 2 ванна 1 (кор. мойка)')
                m.row('cleaning',
                      push_func=AxisPusher(start_from=cast_t('10:00'), validator=CleaningValidator(ordered=False)),
                      size=cast_t('01:15'),
                      label=f'Линия 2 ванна 2 (кор. мойка)')

            lines_df['melting_end'] = lines_df['boilings'].apply(lambda boilings: None if not boilings else boilings[-1]['melting_and_packing']['melting'].y[0])
            lines_df = lines_df.sort_values(by='melting_end')

            for i, row in lines_df.iterrows():
                for j, c in enumerate(row['cleanings']):
                    if j == 0:
                        m.block(c, push_func=AxisPusher(start_from=['last_end', row['melting_end'] + 12], validator=CleaningValidator())) # add hour
                    else:
                        m.block(c, push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()))
                    yield

            # make iterator longer
            for _ in range(5):
                yield

    def f4():
        b = m.row('cleaning',  push_func=AxisPusher(start_from=cast_t('22:00'), validator=CleaningValidator()),
              size=cast_t('01:00'),
              label='Короткая мойка термизатора').block
        assert cast_t('22:00') <= b.x[0] <= cast_t('01:00:10'), "Short cleaning too bad"

    run_order([g3(), f4], order2)

    skus = sum([list(b.props['boiling_group_df']['sku']) for b in schedules['mozzarella']['master']['boiling', True]], [])
    is_bar12_present = '1.2' in [sku.form_factor.name for sku in skus]
    if is_bar12_present:
        m.row('cleaning', push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()),
              size=cast_t('01:20'),
              label='Формовщик')

    return m.root


def make_contour_3(schedules):
    df = utils.optimize(_make_contour_3, lambda b: (-b.y[0], -b.find_one(label='Короткая мойка термизатора').x[0]), schedules)
    return df.iloc[-1]['output']


def make_contour_4(schedules, is_tomorrow_day_off=False):
    m = BlockMaker("4 contour")

    with code('drenators'):

        def _make_drenators(values, cleaning_time, label_suffix='', force_pairs=False):
            # logic
            i = 0
            while i < len(values):
                drenator_id, drenator_end = values[i]
                if i == 0 and not force_pairs:
                    # run first drenator single if not force pairs
                    ids = [str(drenator_id)]
                    block = m.row('cleaning', push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator(ordered=False)),
                                  size=cast_t(cleaning_time),
                                  ids=ids,
                                  label=f'Дренатор {", ".join(ids)}{label_suffix}').block
                else:
                    if i + 1 < len(values) and (force_pairs or values[i + 1][1] <= block.y[0] + 2 and not is_tomorrow_day_off):
                        # run pair
                        ids = [str(drenator_id), str(values[i + 1][0])]
                        block = m.row('cleaning',
                                      push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator(ordered=False)),
                                      size=cast_t(cleaning_time),
                                      ids=ids,
                                      label=f'Дренатор {", ".join(ids)}{label_suffix}').block
                        i += 1
                    else:
                        # run single
                        ids = [str(drenator_id)]
                        block = m.row('cleaning', push_func=AxisPusher(start_from=drenator_end,
                                                                       validator=CleaningValidator(ordered=False)),
                                      size=cast_t(cleaning_time),
                                      ids=[drenator_id],
                                      label=f'Дренатор {", ".join(ids)}{label_suffix}').block
                i += 1

        with code('Main drenators'):
            # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
            values = []
            for boiling in schedules['mozzarella']['master']['boiling', True]:
                drenator = boiling['drenator']
                values.append([drenator.y[0], drenator.props['pouring_line'], drenator.props['drenator_num']])
            df = pd.DataFrame(values, columns=['drenator_end', 'pouring_line', 'drenator_num'])
            df['id'] = df['pouring_line'].astype(int) * 2 + df['drenator_num'].astype(int)
            df = df[['id', 'drenator_end']]
            df['drenator_end'] += 12 + 5 # add hour and 25 minutes of buffer
            df = df.drop_duplicates(subset='id', keep='last')
            df = df.reset_index(drop=True)
            df['id'] = df['id'].astype(int) + 1

            values = df.values.tolist()
            _make_drenators(values, '01:20')

        with code('Non used drenators'):
            values = []
            # run drenators that are not present
            non_used_ids = set(range(1, 9)) - set(df['id'].unique())
            non_used_ids = [str(x) for x in non_used_ids]
            for non_used_id in non_used_ids:
                values.append([non_used_id, cast_t('10:00')])
            _make_drenators(values, '01:05', ' (кор. мойка)', force_pairs=True)

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:30'),
          label='Транспортер + линия кислой сыворотки')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:30'),
          label='Линия кислой сыворотки')

    return m.root


def make_contour_5(schedules, input_tanks=(['4', 60], ['5', 60])):
    m = BlockMaker("5 contour")

    m.row('cleaning', push_func=add_push,
          size=cast_t('01:20'),
          label='Танк концентрата')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Танк концентрата')

    with code('scotta'):
        start_t = cast_t('06:30')
        for id, volume in input_tanks:
            concentration_t = utils.custom_round(volume / 15 * 12, 1, 'ceil')
            start_t += concentration_t
            m.row('cleaning', push_func=AxisPusher(start_from=start_t, validator=CleaningValidator()),
                  size=cast_t('01:20'),
                  label=f'Танк рикотты')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия Ретентата')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия подачи на НФ открыть кран')

    m.row('cleaning', push_func=AxisPusher(start_from=cast_t('09:00'), validator=CleaningValidator(ordered=False)),
          size=cast_t('01:20'),
          label='Линия Концентрата на отгрузку')

    return m.root


def _init_end_time(schedules, department, input_end_time):
    if department not in schedules:
        return

    if schedules[department] != 'manual':
        input_end_time = schedules[department].y[0]
    else:
        input_end_time = cast_t(str(input_end_time)[:-3]) # 21:00:00 -> 21:00 -> 252
    return input_end_time


def make_contour_6(schedules, butter_end_time=None, milk_project_end_time=None):
    m = BlockMaker("6 contour")

    butter_end_time = _init_end_time(schedules, 'butter', butter_end_time)
    milk_project_end_time = _init_end_time(schedules, 'milk_project', milk_project_end_time)

    if 'milk_project' in schedules:
        m.row('cleaning', push_func=add_push,
              x=milk_project_end_time,
              size=cast_t('01:20'),
              label='Линия сырого молока на роникс')

    with code('Танк рикотты 1 внутри дня'):
        ricotta_boilings = list(schedules['ricotta'].iter(cls='boiling'))
        whey_used = 1900 * len(ricotta_boilings)
        if whey_used > 100000:
            m.row('cleaning', push_func=AxisPusher(start_from=cast_t('12:00'), validator=CleaningValidator(ordered=False)),
                  size=cast_t('01:20'),
                  label='Танк рикотты 1')

    with code('cream tanks'):
        if 'mascarpone' in schedules:
            boiling_groups = schedules['mascarpone']['mascarpone_boiling_group', True]
            boiling_group = boiling_groups[-1] if len(boiling_groups) < 4 else boiling_groups[3]
            m.row('cleaning', push_func=AxisPusher(start_from=boiling_group['boiling', True][-1]['boiling_process']['adding_lactic_acid'].y[0] + 12, validator=CleaningValidator(ordered=False)),
                                          size=cast_t('01:20'),
                                          label='Танк сливок') # fourth mascarpone boiling group end + hour

        m.row('cleaning', push_func=AxisPusher(start_from=cast_t('09:00'), validator=CleaningValidator(ordered=False)),
                                      size=cast_t('01:20'),
                                      label='Танк сливок')

    with code('mascarpone'):
        if 'mascarpone' in schedules:
            boiling_groups = schedules['mascarpone']['mascarpone_boiling_group', True]
            boiling_group = boiling_groups[-1]
            m.row('cleaning', push_func=AxisPusher(start_from=boiling_group['boiling', True][-1]['boiling_process']['pumping_off'].y[0] + 6, validator=CleaningValidator(ordered=False)),
                  size=(cast_t('01:20'), 0),
                  label='Маскарпоне')

    ricotta_end = ricotta_boilings[-1]['pumping_out'].y[0] + 12
    m.row('cleaning', push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator(ordered=False)),
          size=cast_t('02:30'),
          label='Линия сладкой сыворотки')

    m.row('cleaning', push_func=AxisPusher(start_from=ricotta_end,
                                           validator=CleaningValidator(ordered=False)),
          size=cast_t('01:20'),
          label='Танк сливок')  # ricotta end + hour

    with code('Танк рикотты 1'):
        if len(ricotta_boilings) < 9:
            end_boiling = ricotta_boilings[-1]
        else:
            end_boiling = ricotta_boilings[-9]

        m.row('cleaning', push_func=AxisPusher(start_from=end_boiling.x[0], validator=CleaningValidator(ordered=False)),
              size=cast_t('01:20'),
              label='Танк рикотты 1')

    for label in ['Линия сливок на подмес рикотта', 'Танк рикотты 3', 'Танк рикотты 2']:
        m.row('cleaning', push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator(ordered=False)),
              size=cast_t('01:20'),
              label=label)

    if 'butter' in schedules:
        m.row('cleaning', push_func=AxisPusher(start_from=butter_end_time, validator=CleaningValidator(ordered=False)),
              size=cast_t('01:20'),
              label='Маслоцех')

    return m.root


def make_schedule(schedules, **kwargs):
    m = BlockMaker("schedule")

    contours = [
        make_contour_1(schedules, milk_project_end_time=kwargs.get('milk_project_end_time'), adygea_end_time=kwargs.get('adygea_end_time')),
        make_contour_2(schedules),
        make_contour_3(schedules),
        make_contour_4(schedules, is_tomorrow_day_off=kwargs.get('is_tomorrow_day_off', False)),
        make_contour_5(schedules, input_tanks=kwargs.get('input_tanks', (['4', 60], ['5', 60]))),
        make_contour_6(schedules, butter_end_time=kwargs.get('butter_end_time'), milk_project_end_time=kwargs.get('milk_project_end_time')),
    ]

    for contour in contours:
        m.col(contour, push_func=add_push)

    return m.root
