from app.imports.runtime import *

from app.models import *
from app.enum import LineName


def get_configuration_time(line_name, sku1, sku2):
    if all(
        [
            line_name == LineName.SALT,
            sku1.form_factor.relative_weight
            != sku2.form_factor.relative_weight,  # todo: better to compare form factors? Делаю так, потому что у палочек бывают разные фф, хотя это одни и те же палочки
            sku1.packers[0].name == sku2.packers[0].name == "Ульма",
        ]
    ):
        return 25
    elif sku1 == sku2:
        return 0
    else:
        return 5


# todo: refactor
def make_configuration_blocks(b1, b2, maker, line_name, between_boilings=False):
    res = []
    for packing_team_id in range(1, 3):
        packings = list(b1.iter(cls="packing", packing_team_id=packing_team_id))
        if not packings:
            continue

        packing1 = packings[0]

        packings = list(b2.iter(cls="packing", packing_team_id=packing_team_id))
        if not packings:
            # todo: refactor
            if between_boilings:
                # add one between boilings anyway
                conf_block = maker.create_block(
                    "packing_configuration",
                    size=[1, 0],
                    packing_team_id=packing_team_id,
                    x=[packing1.y[0], 0],
                )
                res.append(conf_block)
            continue

        packing2 = packings[0]
        sku1 = utils.listify(packing1["process"])[-1].props["sku"]  # last sku
        sku2 = utils.listify(packing2["process"])[0].props["sku"]  # first sku

        conf_time_size = get_configuration_time(line_name, sku1, sku2)
        if between_boilings:
            conf_time_size = max(5, conf_time_size)

        if conf_time_size:
            conf_block = maker.create_block(
                "packing_configuration",
                size=[conf_time_size // 5, 0],
                packing_team_id=packing_team_id,
                x=[packing1.y[0], 0],
            )
            res.append(conf_block)
    return res


def boiling_has_multihead_packing(boiling):
    packings = list(boiling.iter(cls="packing"))
    processes = []
    for packing in packings:
        processes += list(
            packing.iter(
                cls="process", sku=lambda sku: "Мультиголова" in sku.packers[0].name
            )
        )
        if processes:
            return True
    return False
