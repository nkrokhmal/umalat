# fmt: off
from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_boiling(boiling_model):
    m = BlockMaker("boiling", boiling_model=boiling_model)

    bt = utils.delistify(boiling_model.boiling_technologies, single=True)

    m.row("heating", size=bt.heating_time // 5)
    m.row("delay", size=bt.delay_time // 5)
    m.row("protein_harvest", size=bt.protein_harvest_time // 5)
    m.row("abandon", size=bt.abandon_time // 5)

    if not boiling_model.flavoring_agent:
        m.row("pumping_out", size=bt.pumping_out_time // 5)
    else:
        # make pumping_out parallel with abandon
        m.row("pumping_out", push_func=add_push,
              size=bt.pumping_out_time // 5,
              x=m.root["abandon"].y[0] - bt.pumping_out_time // 5)

    steam_value = 900 if not boiling_model.flavoring_agent else 673 # todo: take from parameters

    m.row("steam_consumption", push_func=add_push,
          size=m.root["heating"].size,
          x=0,
          value=steam_value)
    return m.root


def make_boiling_sequence(boiling_group_df):
    m = BlockMaker("boiling_sequence")
    sample_row = boiling_group_df.iloc[0]
    boiling_model = utils.delistify(sample_row['sku'].made_from_boilings, single=True)
    n_tanks = sample_row["tanks"]

    boilings = [make_boiling(boiling_model) for _ in range(n_tanks)]

    m.row(boilings[0], push_func=add_push)

    for b_prev, b in utils.iter_pairs(boilings):
        m.row(b, push_func=add_push, x=b_prev['delay'].x)

    return m.root


def make_boiling_group(boiling_group_df):
    boiling_model = boiling_group_df.iloc[0]["sku"].made_from_boilings[0]
    n_tanks = boiling_group_df.iloc[0]["tanks"]
    group_tanks = boiling_group_df.iloc[0]["group_tanks"]
    first_tank = boiling_group_df.iloc[0]["first_tank"]
    m = BlockMaker(
        "boiling_group",
        skus=boiling_group_df["sku"].tolist(),
        boiling_id=boiling_group_df.iloc[0]["boiling_id"],
        boiling_model=boiling_model,
        n_tanks=n_tanks,
        group_tanks=group_tanks,
        first_tank=first_tank,
    )

    boiling_sequence = make_boiling_sequence(boiling_group_df)
    utils.push(m.root, boiling_sequence)
    analysis_start = utils.listify(boiling_sequence["boiling"])[-1]["abandon"].x[0]
    with m.make("analysis_group", x=(analysis_start, 0), push_func=utils.add_push):
        analysis = utils.delistify(
            boiling_model.analysis
        )  # todo: can bge a list for some reason
        if boiling_model.flavoring_agent:
            m.make("analysis", size=(analysis.analysis_time // 5, 0))
            m.make("preparation", size=(analysis.preparation_time // 5, 0))
            m.make("pumping", size=(analysis.pumping_time // 5, 0))
        else:
            m.make("preparation", size=(analysis.preparation_time // 5, 0))
            m.make("analysis", size=(analysis.analysis_time // 5, 0))
            m.make("pumping", size=(analysis.pumping_time // 5, 0))

    # todo: add to rules
    first_packing_sku = boiling_group_df["sku"].iloc[0]
    if first_packing_sku.weight_netto != 0.5:
        packing_start = m.root["analysis_group"]["pumping"].x[0] + 1
    else:
        packing_start = m.root["analysis_group"]["pumping"].y[0] - 1

    # todo: pauses
    packing_time = sum(
        [
            row["kg"] / row["sku"].packing_speed * 60
            for i, row in boiling_group_df.iterrows()
        ]
    )
    packing_time = int(
        utils.custom_round(packing_time, 5, "ceil", pre_round_precision=1)
    )
    assert packing_time >= 15, "Время паковки должно превышать 15 минут"
    m.make(
        "packing",
        x=(packing_start, 0),
        size=(packing_time // 5, 0),
        push_func=utils.add_push,
    )
    return m.root
