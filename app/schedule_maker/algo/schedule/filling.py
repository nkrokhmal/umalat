from utils_ak.interactive_imports import *

from app.schedule_maker.algo.packing import get_configuration_time


def fill_configurations(maker, blocks):
    res = list(blocks)

    boilings = [b for b in blocks if b.props['class'] == 'boiling']

    iterator = SimpleIterator(boilings)

    for b1 in iterator.iter():
        # find next boiling on the same line
        b2 = None

        for i in range(3):
            b = iterator.forward(i + 1, return_last_if_out=True, update_index=False)
            if b.props['boiling_model'].line.name == b1.props['boiling_model'].line.name:
                b2 = b
        if b2 is None or b1 == b2:
            # finished - nothing to find
            return res

        for packing_team_id in range(1, 3):
            packings = list(b1.iter({'class': "packing", 'packing_team_id': packing_team_id}))
            if not packings:
                continue

            packing1 = packings[0]

            packings = list(b2.iter({'class': "packing", 'packing_team_id': packing_team_id}))
            if not packings:
                continue
            packing2 = packings[0]

            sku1 = listify(packing1['packing_process'])[-1].props['sku']  # last sku
            sku2 = listify(packing2['packing_process'])[0].props['sku']  # first sku

            conf_time_size = get_configuration_time(b1.props['boiling_model'].line.name, sku1, sku2)
            if conf_time_size:
                conf_block = maker.create_block('packing_configuration', size=[conf_time_size // 5, 0], packing_team_id=packing_team_id)
                res.insert(res.index(b1) + 1, conf_block)
    return res

