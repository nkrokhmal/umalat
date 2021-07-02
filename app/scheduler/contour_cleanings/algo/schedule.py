# fmt: off
from app.imports.runtime import *
from utils_ak.block_tree import *
from app.scheduler.time import *


class CleaningValidator(ClassValidator):
    def __init__(self):
        super().__init__(window=10)

    @staticmethod
    def validate__cleaning__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2, distance=2, ordered=True)

def make_contour_3(mozarella_schedule):
    m = BlockMaker("3")

    salt_boilings = [b for b in mozarella_schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']
    if salt_boilings:
        salt_melting_start = salt_boilings[0]['melting_and_packing']['melting']['meltings'].x[0]
        m.row('cleaning', push_func=add_push,
              size=90 // 5, x=salt_melting_start + 6,
              label='Контур циркуляции рассола') # add half hour

    last_full_cleaning_start = mozarella_schedule['master']['cleaning', True][-1].x[0]
    m.row('cleaning', push_func=add_push,
          size=90 // 5, x=last_full_cleaning_start,
          label='Полная мойка термизатора')

    with code('cheese_makers'):
        # get when cheese makers end (values -> [('1', 97), ('0', 116), ('2', 149), ('3', 160)])
        values = []
        for b in mozarella_schedule['master']['boiling', True]:
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

        lines_df.loc['water', 'boilings'] = [b for b in mozarella_schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Моцарелла в воде']
        lines_df.loc['salt', 'boilings'] = [b for b in mozarella_schedule['master']['boiling', True] if b.props['boiling_model'].line.name == 'Пицца чиз']

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
                    b = m.block(c, push_func=AxisPusher(start_from=max(m.root['cleaning', True][-1].y[0], row['melting_end'] + 12), validator=Validator())) # add hour
                else:
                    b = m.block(c, push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()))

                if not filled_short_termizator and cast_time(b.block.y[0]) >= '00:22:00':
                    m.block(short_termizator_cleaning, push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()))

                    filled_short_termizator = True

        if not filled_short_termizator:
            m.block(short_termizator_cleaning, push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()))

    skus = sum([list(b.props['boiling_group_df']['sku']) for b in mozarella_schedule['master']['boiling', True]], [])
    is_bar12_present = '1.2' in [sku.form_factor.name for sku in skus]
    if is_bar12_present:
        m.row('cleaning', push_func=AxisPusher(start_from='last_end', validator=CleaningValidator()),
              size=cast_t('01:20'),
              label='Формовщик')

    return m.root
