from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.schedule_maker.algo.packing import *
from app.schedule_maker.algo.cooling import *


def make_melting_and_packing_basic(boiling_plan):
    boiling_plan = boiling_plan.copy()
    boiling_model = boiling_plan.iloc[0]['boiling']

    boiling_plan['ff'] = boiling_plan['sku'].apply(lambda sku: sku.form_factor)

    # remove Терка from form_factors
    boiling_plan['ff'] = boiling_plan['ff'].apply(lambda ff: ff if ff.name != 'Терка' else None)

    # fill Терка empty form factor values
    boiling_plan['ff'] = boiling_plan['ff'].fillna(method='ffill')
    boiling_plan['ff'] = boiling_plan['ff'].fillna(method='bfill')

    # todo: test
    assert boiling_plan['ff'].any(), 'At least one sku should be non-Терка for now' # todo: make properly

    boiling_plan['ct'] = boiling_plan['ff'].apply(lambda ff: ff.default_cooling_technology)
    boiling_plan['group_key'] = boiling_plan['ff'].astype(str) + boiling_plan['ct'].astype(str)
    mark_consecutive_groups(boiling_plan, 'group_key', 'melting_group')

    maker, make = init_block_maker('melting_and_packing')

    with make('melting'):
        serving = make('serving', size=(boiling_model.line.serving_time // 5, 0), push_func=add_push).block
        meltings = make('meltings', x=(serving.size[0], 0), push_func=add_push).block
        coolings = make('coolings', x=(serving.size[0], 0), push_func=add_push).block

        for i, (group, grp) in enumerate(boiling_plan.groupby('melting_group')):
            # print(group)
            # print(grp)
            if i >= 1 and boiling_model.line.name == LineName.WATER:
                # non-first group - reconfigure time
                push(meltings, maker.create_block('melting_configuration', size=(1, 0)))
                # todo: remove reconfiguration when neighbour form_factors are the same

            ff, ct = grp.iloc[0]['ff'], grp.iloc[0]['ct']

            melting_process = maker.create_block('melting_process',
                                                 size=(int(custom_round(grp['kg'].sum() / boiling_model.line.melting_speed * 60, 5, 'ceil')) // 5, 0),
                                                 ff=ff)

            push(meltings, melting_process)
            cooling_process = make_cooling_process(boiling_model, ct, melting_process.size[0], x=melting_process.props['x_rel'])
            push(coolings, cooling_process, push_func=add_push)

    with make('packing',
              x=(listify(maker.root['melting']['coolings']['cooling_process'])[0]['start'].y[0], 0),
              packing_team_id=1, push_func=add_push):
        for i, (_, row) in enumerate(boiling_plan.iterrows()):
            sku, kg = row['sku'], row['kg']
            packing_speed = min(sku.packing_speed, boiling_model.line.melting_speed)
            make('packing_process',
                 size=[int(custom_round(kg / packing_speed * 60, 5, rounding='ceil')) // 5, 0],
                 sku=sku)

            if i != len(boiling_plan) - 1:
                # add configuration
                conf_time_size = get_configuration_time(boiling_model, sku, boiling_plan.iloc[i + 1]['sku'])

                if conf_time_size:
                    make('packing_configuration', size=[conf_time_size // 5, 0])

    return maker.root


