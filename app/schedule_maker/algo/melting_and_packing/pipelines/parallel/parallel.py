from utils_ak.interactive_imports import *
from app.schedule_maker.models import *

from app.schedule_maker.algo import make_boiling
from app.schedule_maker.algo.packing import *
from app.schedule_maker.algo.cooling import *
from app.schedule_maker.calculation import *
from app.schedule_maker.algo.melting_and_packing.melting_process import make_melting_and_packing_from_mpps

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

    make(make_cooling_process(boiling_model, maker.root['melting_process'].size[0]))

    for packing in maker.root['packing']:
        packing.props.update({'x': [maker.root['cooling_process']['start'].y[0], 0]})

    maker.root.props.update({'kg': boiling_volume})
    return maker.root




def make_boilings_parallel_dynamic(boiling_group_df):
    boilings = []

    boiling_group_df = boiling_group_df.copy()
    boiling_group_df['packing_speed'] = boiling_group_df['sku'].apply(lambda sku: sku.packing_speed)

    # todo: hardcode
    def cast_bff(sku):
        if sku == cast_sku(4):
            return cast_boiling_form_factor(5)
        elif sku == cast_sku(37):
            return cast_boiling_form_factor(8)
        else:
            return sku.boiling_form_factors[0]

    boiling_volumes = [grp['kg'].sum() for i, grp in boiling_group_df.groupby('batch_id')]

    # sum same skus for same teams
    boiling_group_df['sku_name'] = boiling_group_df['sku'].apply(lambda sku: sku.name)
    values = []
    for _, grp in boiling_group_df.groupby(['packing_team_id', 'sku_name']):
        value = grp.iloc[0]
        value['kg'] = grp['kg'].sum()
        values.append(value)
    boiling_group_df = pd.DataFrame(values)
    boiling_group_df.pop('sku_name')
    boiling_group_df = boiling_group_df.sort_values(by='batch_id')

    boiling_group_df['bff'] = boiling_group_df['sku'].apply(cast_bff)
    boiling_group_df['left'] = boiling_group_df['kg']

    boiling_model = boiling_group_df.iloc[0]['boiling']
    ids = remove_duplicates(boiling_group_df['batch_id'].sort_values())
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

        melting_and_packing = make_melting_and_packing_from_mpps(boiling_model, mpps)
        boiling = make_boiling(boiling_model, ids[0] + i, melting_and_packing)
        boilings.append(boiling)
    return boilings