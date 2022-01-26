# fmt: off
from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_boiling(boiling_model):
    m = BlockMaker("boiling", boiling_model=boiling_model)

    bt = utils.delistify(boiling_model.boiling_technologies, single=True) # there is only one boiling technology is for every boiling model in ricotta department

    m.row("heating", size=bt.heating_time // 5)
    m.row("delay", size=bt.delay_time // 5)
    m.row("protein_harvest", size=bt.protein_harvest_time // 5)
    m.row("abandon", size=bt.abandon_time // 5)

    with code('pumping_out'):
        if not boiling_model.flavoring_agent:
            m.row("pumping_out", size=bt.pumping_out_time // 5)
        else:
            # make pumping_out parallel with abandon
            m.row("pumping_out", push_func=add_push,
                  size=bt.pumping_out_time // 5,
                  x=m.root["abandon"].y[0] - bt.pumping_out_time // 5)

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
    first_row = sample_row = boiling_group_df.iloc[0]

    boiling_model = utils.delistify(sample_row["sku"].made_from_boilings, single=True)

    m = BlockMaker("boiling_group",
                   skus=boiling_group_df["sku"].tolist(),
                   boiling_id=sample_row["absolute_batch_id"],
                   boiling_model=boiling_model,
                   n_tanks=sample_row["tanks"],
                   group_tanks=sample_row["group_tanks"],
                   first_tank=sample_row["first_tank"])

    boiling_sequence = make_boiling_sequence(boiling_group_df)

    m.block(boiling_sequence)

    with code('make_analysis'):
        _last_boiling = boiling_sequence["boiling", True][-1]
        analysis_start = _last_boiling["abandon"].x[0]
        with m.row("analysis_group", push_func=add_push, x=analysis_start):
            analysis = utils.delistify(boiling_model.analysis, single=True)

            if boiling_model.flavoring_agent:
                m.row("analysis", size=analysis.analysis_time // 5)
                m.row("preparation", size=analysis.preparation_time // 5)
                m.row("pumping", size=analysis.pumping_time // 5)
            else:
                m.row("preparation", size=analysis.preparation_time // 5)
                m.row("analysis", size=analysis.analysis_time // 5)
                m.row("pumping", size=analysis.pumping_time // 5)

    with code('make_packing'):
        if first_row['sku'].weight_netto != 0.5:
            packing_start = m.root["analysis_group"]["pumping"].x[0] + 1
        else:
            packing_start = m.root["analysis_group"]["pumping"].y[0] - 1

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

        m.row("packing", push_func=add_push,
               x=packing_start,
               size=packing_time // 5)
    return m.root
