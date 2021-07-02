# fmt: off
from app.imports.runtime import *
from utils_ak.block_tree import *
from app.scheduler.time import *


class CleaningValidator(ClassValidator):
    def __init__(self, window=10, ordered=True):
        self.ordered = ordered
        super().__init__(window=window)

    def validate__cleaning__cleaning(self, b1, b2):
        validate_disjoint_by_axis(b1, b2, distance=2, ordered=self.ordered)


def make_contour_3(schedules):
    m = BlockMaker("3")

    salt_boilings = [b for b in schedules['mozzarella']['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']
    if salt_boilings:
        salt_melting_start = salt_boilings[0]['melting_and_packing']['melting']['meltings'].x[0]
        m.row('cleaning', push_func=add_push,
              size=90 // 5, x=salt_melting_start + 6,
              label='Контур циркуляции рассола') # add half hour

    last_full_cleaning_start = schedules['mozzarella']['master']['cleaning', True][-1].x[0]
    m.row('cleaning', push_func=add_push,
          size=90 // 5, x=last_full_cleaning_start,
          label='Полная мойка термизатора')

    with code('cheese_makers'):
        # get when cheese makers end (values -> [('1', 97), ('0', 116), ('2', 149), ('3', 160)])
        values = []
        for b in schedules['mozzarella']['master']['boiling', True]:
            values.append([b.props['pouring_line'], b['pouring'].y[0]])
        df = pd.DataFrame(values, columns=['pouring_line', 'finish'])
        values = df.groupby('pouring_line').agg(max).to_dict()['finish']
        values = list(sorted(values.items(), key=lambda kv: kv[1])) # [('1', 97), ('0', 116), ('2', 149), ('3', 160)]

        for n, cheese_maker_end in values:
            m.row('cleaning', push_func=AxisPusher(start_from=cheese_maker_end, validator=CleaningValidator()),
                  size=cast_t('01:20'),
                  label=f'Сыроизготовитель {int(n) + 1}')

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

        lines_df['melting_end'] = lines_df['boilings'].apply(lambda boilings: None if not boilings else boilings[-1]['melting_and_packing']['melting'].y[0])

        short_termizator_cleaning = m.create_block('cleaning',
                                                   size=(cast_t('01:00'), 0),
                                                   label='Короткая мойка термизатора')
        filled_short_termizator = False

        for i, row in lines_df.iterrows():
            for j, c in enumerate(row['cleanings']):
                if j == 0:
                    b = m.block(c, push_func=AxisPusher(start_from=['last_end', row['melting_end'] + 12], validator=CleaningValidator())) # add hour
                else:
                    b = m.block(c, push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()))

                if not filled_short_termizator and cast_time(b.block.y[0]) >= '00:22:00':
                    m.block(short_termizator_cleaning, push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()))

                    filled_short_termizator = True

        if not filled_short_termizator:
            m.block(short_termizator_cleaning, push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()))

    skus = sum([list(b.props['boiling_group_df']['sku']) for b in schedules['mozzarella']['master']['boiling', True]], [])
    is_bar12_present = '1.2' in [sku.form_factor.name for sku in skus]
    if is_bar12_present:
        m.row('cleaning', push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()),
              size=cast_t('01:20'),
              label='Формовщик')

    return m.root

def make_contour_4(schedules):
    m = BlockMaker("4 contour")

    with code('drenators'):
        # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
        values = []
        for boiling in schedules['mozzarella']['master']['boiling', True]:
            drenator = boiling['drenator']
            values.append([drenator.y[0], drenator.props['pouring_line'], drenator.props['drenator_num']])
        df = pd.DataFrame(values, columns=['drenator_end', 'pouring_line', 'drenator_num'])
        df['id'] = df['pouring_line'].astype(int) * 2 + df['drenator_num'].astype(int)
        df = df[['id', 'drenator_end']]
        df = df.drop_duplicates(subset='id', keep='last')
        df = df.reset_index(drop=True)
        df['id'] = df['id'].astype(int) + 1
        values = df.values.tolist()

        # logic
        i = 0
        while i < len(values):
            drenator_id, drenator_end = values[i]
            if i == 0:
                ids = [str(drenator_id)]
                block = m.row('cleaning', push_func=add_push,
                              size=cast_t('01:20'), x=drenator_end,
                              ids=ids,
                              label=f'Дренатор {", ".join(ids)}').block
            else:
                if i + 1 < len(values) and values[i + 1][1] <= block.y[0] + 2:
                    # clean multiple drenators
                    ids = [str(drenator_id), str(values[i + 1][0])]
                    block = m.row('cleaning',
                                  push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()),
                                  size=cast_t('01:20'),
                                  ids=ids,
                                  label=f'Дренатор {", ".join(ids)}').block
                    i += 1
                else:
                    ids = [str(drenator_id)]
                    block = m.row('cleaning', push_func=AxisPusher(start_from=['last_end', drenator_end],
                                                                   validator=CleaningValidator()),
                                  size=cast_t('01:20'),
                                  ids=[drenator_id],
                                  label=f'Дренатор {", ".join(ids)}').block
            i += 1
        # todo: do not pair before non-working days

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:30'),
          label='Транспортер + линия кислой сыворотки')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:30'),
          label='Линия кислой сыворотки')

    return m.root

def make_contour_1(schedules):
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
                values.append([percent, _boilings[8]])
            values.append([percent, _boilings[-1]])

        df = pd.DataFrame(values, columns=['percent', 'boiling'])
        df['pouring_end'] = df['boiling'].apply(lambda boiling: boiling['pouring']['first']['termizator'].y[0])
        df = df[['percent', 'pouring_end']]
        df = df.sort_values(by='pouring_end')
        values = df.values.tolist()

        for percent, end in values:
            m.row('cleaning', push_func=AxisPusher(start_from=['last_end', end], validator=CleaningValidator()),
                  size=cast_t('01:50'),
                  label=f'Танк смесей {percent}')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия отгрузки')

    # todo soon: add proper start_from
    m.row('cleaning', push_func=AxisPusher(start_from=['last_end'], validator=CleaningValidator()),
          size=cast_t('01:50'),
          label='Линия адыгейского')

    # todo soon: add proper start_from
    m.row('cleaning',
          push_func=AxisPusher(start_from=['last_end', schedules['milk_project'].y[0]], validator=CleaningValidator()),
          size=cast_t('02:20'),
          label='Милкпроджект')

    m.row('cleaning', push_func=AxisPusher(validator=CleaningValidator()),
          size=cast_t('01:20'),
          label='Линия роникс')

    for _ in range(3):
        m.row('cleaning', push_func=AxisPusher(start_from=0, validator=CleaningValidator(ordered=False, window=30)),
              size=cast_t('01:50'),
              label='Танк сырого молока')

    for _ in range(2):
        m.row('cleaning', push_func=AxisPusher(start_from=0, validator=CleaningValidator(ordered=False, window=30)),
              size=cast_t('01:50'),
              label='Танк обрата')

    return m.root
