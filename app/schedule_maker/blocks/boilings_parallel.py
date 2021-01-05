from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.schedule_maker.blocks.boiling import make_boiling
from app.schedule_maker.blocks.packing import *

ERROR = 1e-5


def make_mpp(boiling_df, left_boiling_volume):
    boiling_df['cur_speed'] = 0
    boiling_df['beg_ts'] = None
    boiling_df['end_ts'] = None

    boiling_model = boiling_df.iloc[0]['boiling']
    boiling_volume = min(boiling_df['left'].sum(), left_boiling_volume)
    packing_team_ids = remove_duplicates(boiling_df['packing_team_id'])

    old_ts = 0
    cur_ts = 0

    left = boiling_volume

    assert left < boiling_df['left'].sum() + ERROR  # have enough packers to collect |this volume

    while left > ERROR:
        # get next skus
        cur_skus_values = []
        for packing_team_id in packing_team_ids:
            team_df = boiling_df[(boiling_df['packing_team_id'] == packing_team_id) & (boiling_df['left'] > ERROR)]
            if len(team_df) > 0:
                cur_skus_values.append(team_df.iloc[0])
        cur_skus_df = pd.DataFrame(cur_skus_values).sort_values(by='packing_speed')  # two rows for next packing skus

        # set speeds
        # todo: del
        if boiling_model.boiling_type == 'salt':
            boiling_model.meltings.speed = 850 / 50 * 60

        packing_speed_left = boiling_model.meltings.speed
        for i, cur_sku in cur_skus_df.iterrows():
            cur_speed = min(packing_speed_left, cur_sku['packing_speed'])
            boiling_df.at[cur_sku.name, 'cur_speed'] = cur_speed
            packing_speed_left -= cur_speed

            # set start of packing
            if cur_sku['beg_ts'] is None:
                boiling_df.at[cur_sku.name, 'beg_ts'] = cur_ts

        df = boiling_df[boiling_df['cur_speed'] > 0]

        old_ts = cur_ts
        cur_ts = old_ts + min((df['left'] / df['cur_speed']).min(), left / df['cur_speed'].sum()) * 60  # either one of the skus are collected or the boiling is over

        # update collected kgs
        boiling_df['left'] -= (cur_ts - old_ts) * boiling_df['cur_speed'] / 60
        left -= (cur_ts - old_ts) * boiling_df['cur_speed'].sum() / 60
        boiling_df['cur_speed'] = 0

        boiling_df['end_ts'] = np.where((~boiling_df['beg_ts'].isnull()) & boiling_df['end_ts'].isnull() & (boiling_df['left'] < ERROR), cur_ts, boiling_df['end_ts'])

        assert boiling_df['left'].min() >= -ERROR  # check that all quantities are positive

    # set current time - collected how much we could
    boiling_df['end_ts'] = np.where((~boiling_df['beg_ts'].isnull()) & boiling_df['end_ts'].isnull(), cur_ts, boiling_df['end_ts'])

    def round_timestamps(df, packing_team_ids):
        # todo: hardcode
        # round last end_ts up
        # df.at[df[~df['end_ts'].isnull()].index[-1], 'end_ts'] = custom_round(df.at[df[~df['end_ts'].isnull()].index[-1], 'end_ts'], 5, 'ceil')

        # round to five-minute intervals
        df['beg_ts'] = df['beg_ts'].apply(lambda ts: None if ts is None else custom_round(ts, 5))
        df['end_ts'] = df['end_ts'].apply(lambda ts: None if ts is None else custom_round(ts, 5))

        # fix small intervals (like beg_ts and end_ts: 5, 5 -> 5, 10)
        for packing_team_id in packing_team_ids:
            grp = df[boiling_df['packing_team_id'] == packing_team_id]
            grp = grp[~grp['beg_ts'].isnull()]
            cur_fix = 0
            for i, row in grp.iterrows():
                df.at[i, 'beg_ts'] += cur_fix
                if row['beg_ts'] == row['end_ts']:
                    cur_fix += 5
                df.at[i, 'end_ts'] += cur_fix
    round_timestamps(boiling_df, packing_team_ids)

    # create block
    maker, make = init_block_maker('melting_and_packing_process', axis=1)

    # create packing blocks
    for packing_team_id in packing_team_ids:
        with make('packing', packing_team_id=packing_team_id):
            df = boiling_df[boiling_df['packing_team_id'] == packing_team_id]
            df = df[~df['beg_ts'].isnull()]
            for i, (_, row) in enumerate(df.iterrows()):
                # add configuration
                if i >= 1:
                    conf_time_size = get_configuration_time(boiling_model, row['sku'], df.iloc[i - 1]['sku'])
                    if conf_time_size:
                        make('packing_configuration', size=[conf_time_size // 5, 0])
                make('packing_process', size=(custom_round(row['end_ts'] - row['beg_ts'], 5, 'ceil') // 5, 0), sku=row['sku'])
    # get packings max size
    packings_max_size = max([packing.size[0] for packing in listify(maker.root['packing'])])

    make('melting_process', size=(packings_max_size, 0), bff=boiling_df.iloc[0]['bff'])

    with make('cooling_process'):
        with make('start'):
            if boiling_model.boiling_type == 'water':
                make('cooling', size=(boiling_model.meltings.first_cooling_time // 5, 0))
                make('cooling', size=(boiling_model.meltings.second_cooling_time // 5, 0))
            elif boiling_model.boiling_type == 'salt':
                make('salting', size=(boiling_model.meltings.salting_time // 5, 0))
        with make('finish'):
            if boiling_model.boiling_type == 'water':
                make('cooling', size=(maker.root['melting_process'].size[0], 0))
            elif boiling_model.boiling_type == 'salt':
                make('salting', size=(maker.root['melting_process'].size[0], 0))

    for packing in maker.root['packing']:
        packing.props.update({'x': [maker.root['cooling_process']['start'].y[0], 0]})

    maker.root.props.update({'kg': boiling_volume})
    return maker.root


from itertools import product


def _make_melting_and_packing_from_mpps(boiling_model, mpps):
    maker, make = init_block_maker('melting_and_packing', axis=0)

    class_validator = ClassValidator(window=3)
    def validate(b1, b2):
        validate_disjoint_by_axis(b1['melting_process'], b2['melting_process'])

        for p1, p2 in product(b1.iter({'class': 'packing_team'}), b2.iter({'class': 'packing_team'})):
            if p1.props['packing_team_id'] != p2.props['packing_team_id']:
                continue
            validate_disjoint_by_axis(p1, p2)
    class_validator.add('melting_and_packing_process', 'melting_and_packing_process', validate)

    def validate(b1, b2):
        b1, b2 = list(sorted([b1, b2], key=lambda b: b.props['class'])) # melting_and_packing_process, packing_configuration

        if b1.props['packing_team_id'] != b2.props['packing_team_id']:
            return
        packings = list(b1.iter({'class': "packing", 'packing_team_id': b2.props['packing_team_id']}))
        if not packings:
            return
        packing = packings[0]
        validate_disjoint_by_axis(packing, b2)
    class_validator.add('melting_and_packing_process', 'packing_configuration', validate, uni_direction=True)

    # add configurations if necessary
    blocks = [mpps[0]]
    for i in range(len(mpps) - 1):
        mpp1, mpp2 = mpps[i: i + 2]

        for packing_team_id in range(1, 3):
            packings = list(mpp1.iter({'class': "packing", 'packing_team_id': packing_team_id}))
            if not packings:
                continue
            packing1 = packings[0]

            packings = list(mpp2.iter({'class': "packing", 'packing_team_id': packing_team_id}))
            if not packings:
                continue
            packing2 = packings[0]

            sku1 = listify(packing1['packing_process'])[-1].props['sku'] # last sku
            sku2 = listify(packing2['packing_process'])[0].props['sku'] # first sku

            conf_time_size = get_configuration_time(boiling_model, sku1, sku2)
            if conf_time_size:
                conf_block = maker.create_block('packing_configuration', size=[conf_time_size // 5, 0], packing_team_id=packing_team_id)
                blocks.append(conf_block)

        # add right block
        blocks.append(mpp2)

    for c in blocks:
        push(maker.root, c, push_func=lambda parent, block: dummy_push(parent, block, start_from='last_beg', validator=class_validator))

    mp = maker.root

    maker, make = init_block_maker('melting_and_packing', axis=0, make_with_copy_cut=True)

    with make('melting'):
        serving = make('serving', size=(boiling_model.meltings.serving_time // 5, 0), push_func=add_push).block

        with make('meltings', x=(serving.size[0], 0), push_func=add_push):
            for i, block in enumerate(listify(mp['melting_and_packing_process'])):
                make('melting_process', size=(block['melting_process'].size[0], 0),
                     bff=block['melting_process'].props['bff'])

        with make('coolings', x=(serving.size[0], 0), push_func=add_push):
            for i, block in enumerate(listify(mp['melting_and_packing_process'])):
                make(block['cooling_process'], push_func=add_push)

    for packing_team_id in range(1, 3):
        # todo: hardcode
        all_packing_processes = list(listify(mp['melting_and_packing_process'])[0].iter({'class': 'packing_process', 'packing_team_id': packing_team_id}))

        if all_packing_processes:
            with make('packing', x=(all_packing_processes[0].x[0] + maker.root['melting']['meltings'].x[0], 0),
                      packing_team_id=packing_team_id, push_func=add_push):
                for block in mp.children:
                    if block.props['class'] == 'packing_configuration':
                        make('packing_configuration', size=(block.size[0], 0))
                    elif block.props['class'] == 'melting_and_packing_process':
                        # get our packing
                        packings = list(block.iter({'class': 'packing', 'packing_team_id': packing_team_id}))
                        if not packings:
                            continue
                        packing = packings[0]

                        for b in packing.children:
                            if b.props['class'] == 'packing_process':
                                make(b.props['class'], size=(b.size[0], 0), sku=b.props['sku'])
                            elif b.props['class'] == 'packing_configuration':
                                make(b.props['class'], size=(b.size[0], 0))
    return maker.root


def make_boilings_parallel_dynamic(boiling_group_df):
    boilings = []

    boiling_group_df = boiling_group_df.copy()
    boiling_group_df['packing_speed'] = boiling_group_df['sku'].apply(lambda sku: sku.packing_speed)

    # todo: hardcode
    def cast_bff(sku):
        if sku == cast_sku(4):
            return cast_boiling_form_factor(5)
        else:
            return sku.boiling_form_factors[0]

    boiling_volumes = [grp['kg'].sum() for i, grp in boiling_group_df.groupby('id')]

    # sum same skus for same teams
    boiling_group_df['sku_name'] = boiling_group_df['sku'].apply(lambda sku: sku.name)
    values = []
    for _, grp in boiling_group_df.groupby(['packing_team_id', 'sku_name']):
        value = grp.iloc[0]
        value['kg'] = grp['kg'].sum()
        values.append(value)
    boiling_group_df = pd.DataFrame(values)
    boiling_group_df.pop('sku_name')
    boiling_group_df = boiling_group_df.sort_values(by='id')

    boiling_group_df['bff'] = boiling_group_df['sku'].apply(cast_bff)
    boiling_group_df['left'] = boiling_group_df['kg']

    boiling_model = boiling_group_df.iloc[0]['boiling']
    ids = remove_duplicates(boiling_group_df['id'].sort_values())
    form_factors = remove_duplicates(boiling_group_df['bff'])

    cur_form_factor = form_factors[0]
    cur_boiling_df = boiling_group_df[boiling_group_df['bff'] == cur_form_factor]
    for i, boiling_volume in enumerate(boiling_volumes):
        mpps = []

        left = boiling_volume

        while left > ERROR:
            # get next cur_boiling_df if necessary
            if cur_boiling_df['left'].sum() < ERROR:
                assert form_factors.index(cur_form_factor) + 1 < len(form_factors)  # check there are form factors left
                cur_form_factor = form_factors[form_factors.index(cur_form_factor) + 1]
                cur_boiling_df = boiling_group_df[boiling_group_df['bff'] == cur_form_factor]

            mpp = make_mpp(cur_boiling_df, left)
            mpps.append(mpp)
            left -= mpp.props['kg']

        melting_and_packing = _make_melting_and_packing_from_mpps(boiling_model, mpps)
        boiling = make_boiling(boiling_model, ids[0] + i, melting_and_packing)
        boilings.append(boiling)
    return boilings



def test1():
    def cast_bff(sku):
        if sku == cast_sku(4):
            return cast_boiling_form_factor(5)
        else:
            return sku.boiling_form_factors[0]

    from app.schedule_maker.dataframes import read_boiling_plan
    boiling_plan_df = read_boiling_plan(r"C:\Users\Mi\YandexDisk\Shared\2020 umalat\schedules\2020.12.15_boiling_plan.xlsx")
    # boiling_plan_df['packing_team_id'] = pd.read_csv('boiling_plan.csv', sep=';')['packing_team_id']
    mark_consecutive_groups(boiling_plan_df, 'boiling', 'boiling_group')

    for _, grp in boiling_plan_df.groupby('boiling_group'):
        grp['packing_speed'] = grp['sku'].apply(lambda sku: sku.packing_speed)
        grp['bff'] = grp['sku'].apply(cast_bff)
        display(grp)
        boilings = make_boilings_parallel_dynamic(grp)
        for boiling in boilings:
            mp = boiling['melting_and_packing']
            mp.props.update({'x': (0, 0)})
            display(mp)

def test2():
    mark_consecutive_groups(boiling_plan_df, 'boiling', 'boiling_group')

    grp = boiling_plan_df[boiling_plan_df['boiling_group'] == 3]

    grp['packing_speed'] = grp['sku'].apply(lambda sku: sku.packing_speed)
    grp['bff'] = grp['sku'].apply(cast_bff)
    display(grp)
    boilings = make_boilings_parallel_dynamic(grp)
    for boiling in boilings:
        print(boiling.props['boiling_id'])
        mp = boiling['melting_and_packing']
        mp.props.update({'x': (0, 0)})
        display(mp)


def test3():
    boiling_plan_df['bff'] = boiling_plan_df['sku'].apply(cast_bff)

    boiling_df = boiling_plan_df[boiling_plan_df['bff'] == cast_boiling_form_factor(14)]
    boiling_df['sku_name'] = boiling_df['sku'].apply(lambda sku: sku.name)

    values = []
    for _, grp in boiling_df.groupby(['packing_team_id', 'sku_name']):
        value = grp.iloc[0]
        value['kg'] = grp['kg'].sum()
        values.append(value)
    boiling_df = pd.DataFrame(values)
    boiling_df.pop('sku_name')

    boiling_df['left'] = boiling_df['kg']
    boiling_df['packing_speed'] = boiling_df['sku'].apply(lambda sku: sku.packing_speed)

    boiling_df

    make_mpp(boiling_df, 850)
    boiling_df