from itertools import product
from utils_ak.block_tree import *
from utils_ak.builtin import listify
from app.schedule_maker.algo.packing import get_configuration_time

# todo: refactor?
def make_melting_and_packing_from_mpps(boiling_model, mpps):
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
        serving = make('serving', size=(boiling_model.line.serving_time // 5, 0), push_func=add_push).block

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
