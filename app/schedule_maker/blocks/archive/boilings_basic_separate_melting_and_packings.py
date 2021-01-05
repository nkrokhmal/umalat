from app.schedule_maker import *
from itertools import product
from utils_ak.interactive_imports import *


def make_melting_and_packing_process(boiling_model, bff_group):
    grp = bff_group

    maker, make = init_block_maker('melting_and_packing_process', axis=1)

    make('melting_process',
         size=(custom_round(grp['kg'].sum() / boiling_model.meltings.speed * 60, 5, 'ceil') // 5, 0),
         bff=grp.iloc[0]['bff'], push_func=add_push)

    with make('cooling_process', x=maker.root['melting_process'].props['x_rel']):
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

    with make('packing',
              x=(listify(maker.root['cooling_process'])[0]['start'].y[0], 0),
              packing_team_id=grp.iloc[0]['packing_team_id'], push_func=add_push):
        for i, (_, row) in enumerate(grp.iterrows()):
            sku, kg = row['sku'], row['kg']
            packing_speed = min(sku.packing_speed, boiling_model.meltings.speed)

            make('packing_process', size=[custom_round(kg / packing_speed * 60, 5, rounding='ceil') // 5, 0])

            if i != len(grp) - 1:
                # add configuration
                new_sku = grp.iloc[i + 1]['sku']
                conf_time_size = 0
                if boiling_model.boiling_type == 'salt' and sku.weight_form_factor != new_sku.weight_form_factor and cast_packer(sku) == cast_packer(new_sku):
                    # todo: take from parameters
                    conf_time_size = 25
                elif sku == new_sku:
                    conf_time_size = 0
                else:
                    # todo: take from parameters
                    conf_time_size = 5

                if conf_time_size:
                    make('configuration', size=[conf_time_size // 5, 0])
    return maker.root

def make_boilings_basic(boiling_plan_df):
    boiling_plan_df['packing_speed'] = boiling_plan_df['sku'].apply(lambda sku: sku.packing_speed)
    boiling_plan_df['bff'] = boiling_plan_df['sku'].apply(lambda sku: sku.boiling_form_factors[0])

    # todo: make properly
    boiling_plan_df.at[:, 'packing_team_id'] = 1

    def mark_sequent_groups(df, key, groups_key):
        cur_value = None
        cur_i = 0

        values = []
        for i, row in df.iterrows():
            if row[key] != cur_value:
                cur_i += 1
                cur_value = row[key]
            values.append(cur_i)
        df[groups_key] = values

    mark_sequent_groups(boiling_plan_df, 'boiling', 'boiling_group')
    mark_sequent_groups(boiling_plan_df, 'bff', 'bff_group')

    boilings = []

    for boiling_id, boiling_plan in boiling_plan_df.groupby('id'):
        boiling_model = boiling_plan.iloc[0]['boiling']

        if boiling_model.boiling_type == 'salt':
            boiling_model.meltings.speed = 850 / 50 * 60

        maker, make = init_block_maker('root')

        termizator = db.session.query(Termizator).first()

        with make('boiling', boiling_id=boiling_id, boiling_model=boiling_model):
            with make('pouring'):
                with make('first'):
                    make('termizator', size=(termizator.pouring_time // 5, 0))
                    make('fermenting', size=(boiling_model.pourings.pouring_time // 5 - termizator.pouring_time // 5, 0))
                    make('soldification', size=(boiling_model.pourings.soldification_time // 5, 0))
                    make('cutting', size=(boiling_model.pourings.cutting_time // 5, 0))
                with make('second'):
                    make('pouring_off', size=(boiling_model.pourings.pouring_off_time // 5, 0))
                    make('extra', size=(boiling_model.pourings.extra_time // 5, 0))

            make('drenator',
                 x=(maker.root['boiling']['pouring']['first'].y[0], 0),
                 size=(boiling_model.lines.cheddarization_time // 5, 0),
                 push_func=add_push)

            mpps = []
            for i, (group, grp) in enumerate(boiling_plan.groupby('bff_group')):
                mpps.append(make_melting_and_packing_process(boiling_model, grp))

            # add configuration
            mp_line = [mpps[0]]
            for i in range(len(mpps) - 1):
                mpp1, mpp2 = mpps[i: i + 2]
                if boiling_model.boiling_type == 'water':
                    mp_line.append(maker.create_block('melting_configuration', size=(1, 0)))
                mp_line.append(mpp2)

            # create melting_and_packing block

            class_validator = ClassValidator(window=3)

            def validate(b1, b2):
                validate_disjoint_by_axis(b1['melting_process'], b2['melting_process'])

                for p1, p2 in product(b1.iter({'class': 'packing'}), b2.iter({'class': 'packing'})):
                    if p1.props['packing_team_id'] != p2.props['packing_team_id']:
                        continue

                    validate_disjoint_by_axis(p1, p2)

            class_validator.add('melting_and_packing_process', 'melting_and_packing_process', validate)

            def validate(b1, b2):
                validate_disjoint_by_axis(b1, b2['melting_process'])
            class_validator.add('serving', 'melting_and_packing_process', validate)

            def validate(b1, b2):
                b1, b2 = sorted([b1, b2], key=lambda b: b.props['class'])  # 'melting_and_packing and melting_configuration'
                validate_disjoint_by_axis(b1['melting_process'], b2)

            class_validator.add('melting_and_packing_process', 'melting_configuration', validate, uni_direction=True)

            melting_and_packing = maker.create_block('melting_and_packing')
            push(melting_and_packing, maker.create_block('serving', size=(boiling_model.meltings.serving_time // 5, 0)))
            for mp_block in mp_line:
                push(melting_and_packing, mp_block, push_func=lambda parent, block: dummy_push(parent, block, start_from='last_beg', validator=class_validator))
            push(maker.root['boiling'], melting_and_packing)

        boilings.append(maker.root['boiling'])
    return boilings

