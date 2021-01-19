from app.schedule_maker.models import *
from app.enum import LineName


def get_configuration_time(line_name, sku1, sku2):
    if all([line_name == LineName.SALT,
            sku1.form_factor.relative_weight != sku2.form_factor.relative_weight, # todo: better to compare form factors? Делаю так, потому что у палочек бывают разные фф, хотя это одни и те же палочки
            sku1.packer == sku2.packer,
            sku1.packer.name == 'Ульма',
            sku2.packer.name == 'Ульма']):
        return 25
    elif sku1 == sku2:
        return 0
    else:
        return 5


def make_configuration_blocks(b1, b2, maker, line_name):
    res = []
    for packing_team_id in range(1, 3):
        packings = list(b1.iter(cls='packing', packing_team_id=packing_team_id))
        if not packings:
            continue

        packing1 = packings[0]

        packings = list(b2.iter(cls='packing', packing_team_id=packing_team_id))
        if not packings:
            continue
        packing2 = packings[0]
        sku1 = listify(packing1['packing_process'])[-1].props['sku']  # last sku
        sku2 = listify(packing2['packing_process'])[0].props['sku']  # first sku

        conf_time_size = get_configuration_time(line_name, sku1, sku2)
        if conf_time_size:
            conf_block = maker.create_block('packing_configuration', size=[conf_time_size // 5, 0], packing_team_id=packing_team_id, x=[packing1.y[0], 0])
            res.append(conf_block)
    return res