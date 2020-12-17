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
    # prepare boiling_contents from boiling_plan
    values = []
    for i, grp in boiling_plan_df.groupby('id'):
        boiling = grp['boiling'].iloc[0]
        boiling_contents = [[row['sku'], row['kg']] for i, row in grp.iterrows()]
        values.append([boiling, boiling_contents])
    boiling_plan_grouped_df = pd.DataFrame(values, columns=['boiling', 'contents'])
    boiling_plan_grouped_df['used'] = False
    boiling_plan_grouped_df['type'] = boiling_plan_grouped_df['boiling'].apply(lambda b: 'salt' if b.lines.name == 'Пицца чиз' else 'water')
    boiling_plan_grouped_df['id'] = boiling_plan_grouped_df['boiling'].apply(lambda b: int(b.id))

    line_df = pd.DataFrame(index=['water', 'salt'], columns=['iter_props', 'last_packing_sku', 'latest_boiling', 'start_time', 'boilings'])
    line_df.at['water', 'iter_props'] = [{'pouring_line': str(v)} for v in [0, 1]]
    line_df.at['salt', 'iter_props'] = [{'pouring_line': str(v)} for v in [2, 3]]

    # [cheesemakers.start_time]
    line_df.at['water', 'start_time'] = '09:50'
    line_df.at['salt', 'start_time'] = '07:05'

    line_df.at['water', 'boilings'] = []
    line_df.at['salt', 'boilings'] = []

    line_df['last_packing_sku'] = None
    line_df['latest_boiling'] = None

    root = Block('root')
    root.line_df = line_df

    def add_new_boiling(i, boiling_type, init=False):
        row = pick(boiling_plan_grouped_df, boiling_type)
        if row is None:
            return
        b = make_boiling(cast_boiling(str(row['id'])), row['contents'], block_num=i + 1, last_packing_sku=line_df.at[boiling_type, 'last_packing_sku'])

        if init:
            beg = cast_t(line_df.at[boiling_type, 'start_time']) - b['melting_and_packing'].beg
        else:
            beg = line_df.at[row['type'], 'latest_boiling'].beg
        b = dummy_push(root, b, iter_props=line_df.at[boiling_type, 'iter_props'], validator=boiling_validator, beg=beg, max_tries=100)
        line_df.at[boiling_type, 'last_packing_sku'] = list([sku for sku, sku_kg in row['contents']])[-1]
        line_df.at[boiling_type, 'latest_boiling'] = b if not line_df.at[boiling_type, 'latest_boiling'] else max([line_df.at[boiling_type, 'latest_boiling'], b], key=lambda b: b.beg)
        line_df.at[boiling_type, 'boilings'].append(b)

    add_new_boiling(0, 'water', init=True)
    add_new_boiling(1, 'salt', init=True)

    latest_boiling = max(line_df['latest_boiling'], key=lambda b: b.beg)
    last_cleaning_t = latest_boiling.beg

    cur_i = 2

    while True:
        logging.info('Fitting block {}'.format(cur_i))

        left_df = boiling_plan_grouped_df[~boiling_plan_grouped_df['used']]
        left_unique = left_df['type'].unique()

        if len(left_unique) == 1:
            boiling_type = left_unique[0]

            if boiling_type == 'salt':
                # start working for 3 lines on salt
                # [lines.extra_salt_cheesemaker]
                # line_df.at['salt', 'iter_props'] = [{'pouring_line': str(v)} for v in [1, 2, 3]]
                pass
        elif len(left_unique) == 0:
            # stop production
            break
        else:
            latest_boiling = max(line_df['latest_boiling'], key=lambda b: b.beg)
            # choose different line
            boiling_type = 'water' if latest_boiling.props['boiling_type'] == 'salt' else 'salt'

        add_new_boiling(cur_i, boiling_type)

        cur_i += 1

        # [termizator.cleaning]
        # add cleaning if necessary
        boilings = [node for node in root.children if node.props['class'] == 'boiling']
        a, b = list(boilings[-2:])

        rest = b['pouring'][0]['termizator'].beg - a['pouring'][0]['termizator'].end
        if 12 <= rest < 18:
            # [termizator.cleaning.1]
            cleaning = make_termizator_cleaning_block('short')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].beg - cleaning.length})
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end
        elif rest >= 18:
            # [termizator.cleaning.2]
            cleaning = make_termizator_cleaning_block('full')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].beg - cleaning.length})
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end

        # add cleaning if working more than 12 hours without cleaning
        if b['pouring'][0]['termizator'].end - last_cleaning_t > cast_t('12:00'):
            # [termizator.cleaning.3]
            cleaning = make_termizator_cleaning_block('short')
            cleaning.props.update({'t': b['pouring'][0]['termizator'].end})

            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end + cleaning.length


    # add final cleaning [termizator.cleaning.4]
    cleaning = make_termizator_cleaning_block('full')
    boilings = [node for node in root.children if node.props['class'] == 'boiling']
    cleaning.props.update({'t': boilings[-1]['pouring'][0]['termizator'].end + 1}) # add five minutes extra
    add_push(root, cleaning)

    root.props.update({'size': max(c.end for c in root.children)})
    return root


def draw_workbook(root, mode='prod', template_fn=None):
    style = load_style()
    root.props.update({'size': max(c.end for c in root.children)})
    init_sheet_func = init_sheet if mode == 'dev' else init_template_sheet(template_fn=template_fn)
    return draw_schedule(root, style, init_sheet_func=init_sheet_func)
