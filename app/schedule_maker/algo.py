import anyconfig
from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.schedule_maker.utils import *
from app.schedule_maker.validation import *
from app.schedule_maker.blocks import *
from app.schedule_maker.style import *
from itertools import product


def gen_request_df(request):
    values = []
    for boiling in request['Boilings']:
        for sku_id, sku_kg in boiling['SKUVolumes'].items():
            values.append([boiling['BoilingId'], sku_id, sku_kg])
    df = pd.DataFrame(values)

    values = []
    for boiling_id, boiling_grp in df.groupby(0):
        boiling_dic = boiling_grp[[1, 2]].set_index(1).to_dict(orient='index')
        boiling_dic = {k: v[2] for k, v in boiling_dic.items()}  # {'34': 1110.0, '35': 0.0, ...}
        total_kg = sum(boiling_dic.values())

        # round to get full
        # todo: proper logic
        total_kg = custom_round(total_kg, 850, rounding='floor')

        n_boilings = int(total_kg / 850)
        for i in range(n_boilings):
            cur_kg = 850
            boiling_request = {}
            for k, v in list(boiling_dic.items()):
                boil_kg = min(cur_kg, boiling_dic[k])

                boiling_dic[k] -= boil_kg
                cur_kg -= boil_kg

                if k not in boiling_request:
                    boiling_request[k] = 0
                boiling_request[k] += boil_kg

                if cur_kg == 0:
                    break

            if cur_kg != 0:
                # any non-zero
                print('Non-zero')
                k = [k for k, v in boiling_request.items() if v != 0][0]
                boiling_request[k] += cur_kg

            boiling_request = {k: v for k, v in boiling_request.items() if v != 0}
            values.append([boiling_id, boiling_request])
    df = pd.DataFrame(values, columns=['boiling_id', 'request'])
    df['boiling_id'] = df['boiling_id'].astype(str)
    df['boiling_type'] = df['boiling_id'].apply(lambda boiling_id: 'salt' if str(cast_boiling(boiling_id).percent) == '2.7' else 'water')
    df['used'] = False

    return df


def pick(df, boiling_type):
    tmp = df
    tmp = tmp[tmp['used'] == False]
    tmp = tmp[tmp['boiling_type'] == boiling_type]

    if len(tmp) == 0:
        return

    row = tmp.iloc[0]
    df.loc[row.name, 'used'] = True
    return row


def make_schedule(request, date):
    df = gen_request_df(request)

    # draw salt and water
    root = Block('root')

    # add cleanings
    root.rel_props['props_mode'] = 'absolute'
    root.upd_abs_props()

    def make_boiling_row(i, row):
        return make_boiling(cast_boiling(row['boiling_id']), {cast_sku(k): v for k, v in row['request'].items()}, row['boiling_type'], block_num=i + 1)

    iter_water_props = [{'pouring_line': str(v)} for v in [0, 1]]
    iter_salt_props_2 = [{'pouring_line': str(v[0]), 'melting_line': str(v[1])} for v in product([2, 3], [0, 1, 2, 3])]
    iter_salt_props_3 = [{'pouring_line': str(v[0]), 'melting_line': str(v[1])} for v in product([1, 2, 3], [0, 1, 2, 3])]
    iter_salt_props = iter_salt_props_2

    i, row = 0, pick(df, 'water')
    b = make_boiling_row(i, row)
    beg = cast_t('08:00') - b['melting_and_packing'].beg
    dummy_push(root, b, iter_props=iter_water_props, validator=boiling_validator, beg=beg, max_tries=100)

    # init last cleaning with termizator first start
    last_cleaning_t = beg

    i, row = 1, pick(df, 'salt')
    b = make_boiling_row(i, row)
    beg = cast_t('08:20') - b['melting_and_packing'].beg
    dummy_push(root, b, iter_props=iter_salt_props, validator=boiling_validator, beg=beg, max_tries=100)

    boiling_types = ['water', 'salt']
    cur_type_i = -1
    cur_i = 2

    while True:
        cur_type_i = (cur_type_i + 1) % 2
        boiling_type = boiling_types[cur_type_i]
        row = pick(df, boiling_type)

        # todo: make properly
        if row is None:
            if boiling_type == 'water':
                # start working for 3 lines on salt
                iter_salt_props = iter_salt_props_3
                continue
            elif boiling_type == 'salt':
                # stop production when salt is finished
                break
        b = make_boiling_row(cur_i, row)

        iter_props = iter_water_props if boiling_type == 'water' else iter_salt_props
        dummy_push(root, b, iter_props=iter_props, validator=boiling_validator, beg='last_beg', max_tries=100)
        cur_i += 1

        # add cleaning if necessary
        boilings = [node for node in root.children if node.props['class'] == 'boiling']
        a, b = list(boilings[-2:])
        a.upd_abs_props()
        b.upd_abs_props()
        rest = b['pouring'][0]['termizator'].beg - a['pouring'][0]['termizator'].end
        if 12 <= rest < 18:
            cleaning = make_termizator_cleaning_block('short')
            cleaning.rel_props['t'] = b['pouring'][0]['termizator'].beg - cleaning.size
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end
        elif rest >= 18:
            cleaning = make_termizator_cleaning_block('full')
            cleaning.rel_props['t'] = b['pouring'][0]['termizator'].beg - cleaning.size
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end

        # add cleaning if working more than 12 hours without cleaning
        if b['pouring'][0]['termizator'].end - last_cleaning_t > cast_t('12:00'):
            cleaning = make_termizator_cleaning_block('short')
            cleaning.rel_props['t'] = b['pouring'][0]['termizator'].end
            add_push(root, cleaning)
            last_cleaning_t = b['pouring'][0]['termizator'].end + cleaning.size

    # add final cleaning
    cleaning = make_termizator_cleaning_block('full')
    boilings = [node for node in root.children if node.props['class'] == 'boiling']
    cleaning.rel_props['t'] = boilings[-1]['pouring'][0]['termizator'].end + 1  # add five minutes extra
    add_push(root, cleaning)

    root.rel_props.pop('props_mode')
    root.upd_abs_props()

    root.rel_props['size'] = max(c.end for c in root.children)

    return root


# todo: better naming
@clockify()
def draw_workbook(root, mode='prod', template_fn=None):
    style = load_style(mode=mode)
    root.rel_props['size'] = max(c.end for c in root.children)
    init_sheet_func = init_sheet if mode == 'dev' else init_template_sheet(template_fn=template_fn)
    return draw_schedule(root, style, init_sheet_func=init_sheet_func)