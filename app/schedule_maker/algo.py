import anyconfig
from utils_ak.interactive_imports import *
from app.schedule_maker.utils import *
from app.schedule_maker.validation import *
from app.schedule_maker.blocks import *
from app.schedule_maker.style import *
from app.schedule_maker.models import *

from itertools import product


def pick(df, boiling_type):
    tmp = df
    tmp = tmp[tmp['used'] == False]
    tmp = tmp[tmp['type'] == boiling_type]

    if len(tmp) == 0:
        return

    row = tmp.iloc[0]
    df.loc[row.name, 'used'] = True
    return row


def make_schedule(boiling_plan_df):
    values = []
    for i, grp in boiling_plan_df.groupby('id'):
        boiling = grp['boiling'].iloc[0]
        boiling_contents = [[row['sku'], row['kg']] for i, row in grp.iterrows()]
        values.append([boiling, boiling_contents])
    boiling_plan_grouped_df = pd.DataFrame(values, columns=['boiling', 'contents'])
    boiling_plan_grouped_df['used'] = False
    boiling_plan_grouped_df['type'] = boiling_plan_grouped_df['boiling'].apply(lambda b: 'salt' if b.percent == '2.7' else 'water')
    boiling_plan_grouped_df['id'] = boiling_plan_grouped_df['boiling'].apply(lambda b: int(b.id))

    root = Block('root')
    root.boilings_by_line = {'water': [], 'salt': []}

    def make_boiling_row(i, row, last_packing_sku):
        return make_boiling(cast_boiling(str(row['id'])), row['contents'], row['type'], block_num=i + 1, last_packing_sku=last_packing_sku)

    iter_water_props = [{'pouring_line': str(v)} for v in [0, 1]]
    iter_salt_props_2 = [{'pouring_line': str(v[0]), 'melting_line': str(v[1])} for v in product([2, 3], [0, 1, 2, 3])]
    # [lines.extra_salt_cheesemaker]
    iter_salt_props_3 = [{'pouring_line': str(v[0]), 'melting_line': str(v[1])} for v in product([1, 2, 3], [0, 1, 2, 3])]
    iter_salt_props = iter_salt_props_2

    last_packing_skus = {} # {boiling_type: last_packing_sku}

    # will be initialized one of the two first blocks
    last_cleaning_t = None

    latest_water_boiling = None
    latest_salt_boiling = None
    latest_boiling = None

    # [cheesemakers.start_time]
    water_start_time = '09:50'
    salt_start_time = '07:05'

    i, row = 0, pick(boiling_plan_grouped_df, 'water')
    if row is not None:
        # there is water boiling today
        b = make_boiling_row(i, row, None)
        beg = cast_t(water_start_time) - b['melting_and_packing'].beg
        boiling = dummy_push(root, b, iter_props=iter_water_props, validator=boiling_validator, beg=beg, max_tries=100)
        last_packing_skus[row['type']] = list([sku for sku, sku_kg in row['contents']])[-1]

        # init last cleaning with termizator first start
        last_cleaning_t = last_cleaning_t if last_cleaning_t else beg
        latest_boiling = boiling if not latest_boiling else max([latest_boiling, boiling], key=lambda boiling: boiling.beg)
        latest_water_boiling = boiling
        root.boilings_by_line[row['type']].append(boiling)

    i, row = 1, pick(boiling_plan_grouped_df, 'salt')
    if row is not None:
        # there is a salt boiling today
        b = make_boiling_row(i, row, None)
        beg = cast_t(salt_start_time) - b['melting_and_packing'].beg
        boiling = dummy_push(root, b, iter_props=iter_salt_props, validator=boiling_validator, beg=beg, max_tries=100)
        last_packing_skus[row['type']] = list([sku for sku, sku_kg in row['contents']])[-1]

        # init last cleaning with termizator first start
        last_cleaning_t = last_cleaning_t if last_cleaning_t else beg
        latest_boiling = boiling if not latest_boiling else max([latest_boiling, boiling], key=lambda boiling: boiling.beg)
        latest_salt_boiling = boiling
        root.boilings_by_line[row['type']].append(boiling)

    cur_i = 2

    while True:
        # if cur_i == 11:
        #     break

        logging.info('Fitting block {}'.format(cur_i))

        left_df = boiling_plan_grouped_df[~boiling_plan_grouped_df['used']]
        left_unique = left_df['type'].unique()

        if len(left_unique) == 1:
            boiling_type = left_unique[0]

            if boiling_type == 'salt':
                # start working for 3 lines on salt
                # [lines.extra_salt_cheesemaker]
                # iter_salt_props = iter_salt_props_3
                # todo: uncom
                pass
        elif len(left_unique) == 0:
            # stop production
            break
        else:
            # make different block
            boiling_type = 'water' if latest_boiling.props['type'] == 'salt' else 'salt'

        row = pick(boiling_plan_grouped_df, boiling_type)

        beg = latest_water_boiling.beg if boiling_type == 'water' else latest_salt_boiling.beg

        b = make_boiling_row(cur_i, row, last_packing_skus[row['type']])
        iter_props = iter_water_props if boiling_type == 'water' else iter_salt_props
        boiling = dummy_push(root, b, iter_props=iter_props, validator=boiling_validator, beg=int(beg), max_tries=100)
        last_packing_skus[row['type']] = list([sku for sku, sku_kg in row['contents']])[-1]
        latest_boiling = boiling if not latest_boiling else max([latest_boiling, boiling], key=lambda boiling: boiling.beg)
        root.boilings_by_line[row['type']].append(boiling)

        if boiling_type == 'water':
            latest_water_boiling = boiling
        else:
            latest_salt_boiling = boiling

        cur_i += 1

        # [termizator.cleaning]
        # add cleaning if necessary
        boilings = [node for node in root.children if node.props['class'] == 'boiling']
        a, b = list(boilings[-2:])

        rest = b['pouring'][0]['termizator'].beg - a['pouring'][0]['termizator'].end
        if 12 <= rest < 18:
            # [termizator.cleaning.1]
            cleaning = make_termizator_cleaning_block('short')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].beg - cleaning.size})
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end
        elif rest >= 18:
            # [termizator.cleaning.2]
            cleaning = make_termizator_cleaning_block('full')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].beg - cleaning.size})
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end

        # add cleaning if working more than 12 hours without cleaning
        if b['pouring'][0]['termizator'].end - last_cleaning_t > cast_t('12:00'):
            # [termizator.cleaning.3]
            cleaning = make_termizator_cleaning_block('short')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].end})

            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end + cleaning.size

    # add final cleaning [termizator.cleaning.4]
    cleaning = make_termizator_cleaning_block('full')
    boilings = [node for node in root.children if node.props['class'] == 'boiling']

    cleaning.props.update({'t': boilings[-1]['pouring'][0]['termizator'].end + 1}) # add five minutes extra
    add_push(root, cleaning)

    root.props.update({'size': max(c.end for c in root.children)})
    return root


def draw_workbook(root, mode='prod', template_fn=None):
    style = load_style(mode=mode)
    root.props.update({'size': max(c.end for c in root.children)})
    init_sheet_func = init_sheet if mode == 'dev' else init_template_sheet(template_fn=template_fn)
    return draw_schedule(root, style, init_sheet_func=init_sheet_func)
