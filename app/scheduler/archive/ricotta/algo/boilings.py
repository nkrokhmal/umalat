from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push
from utils_ak.builtin.collection import crop_to_chunks, delistify
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.iteration.simple_iterator import iter_pairs
from utils_ak.numeric.numeric import custom_round


# - Utils
def crop_to_chunks(values, n, is_tail_appended=False):
    """Yield successive n-sized chunks from values."""
    tail_size = len(values) % n
    for i in range(0, len(values), n):
        is_penultimate = i == (len(values) - 1) - (tail_size - 1) - n  # last_index - tail_extra - chunk_size
        if is_tail_appended and tail_size != 0 and is_penultimate:
            yield values[i:]
            return
        else:
            yield values[i : i + n]


# - Makers


def make_boiling(boiling_model):
    m = BlockMaker("boiling", boiling_model=boiling_model)

    bt = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in ricotta department

    m.row("heating", size=bt.heating_time // 5)
    m.row("delay", size=bt.delay_time // 5)
    m.row("protein_harvest", size=bt.protein_harvest_time // 5)
    m.row("abandon", size=bt.abandon_time // 5)

    with code("pumping_out"):
        if not boiling_model.flavoring_agent:
            m.row("pumping_out", size=bt.pumping_out_time // 5)
        else:
            # make pumping_out parallel with abandon
            m.row(
                "pumping_out",
                push_func=add_push,
                size=bt.pumping_out_time // 5,
                x=m.root["abandon"].y[0] - bt.pumping_out_time // 5,
            )

    return m.root


def make_boiling_sequence(boiling_group_df):
    m = BlockMaker("boiling_sequence")
    sample_row = boiling_group_df.iloc[0]
    boiling_model = delistify(sample_row["sku"].made_from_boilings, single=True)
    n_tanks = sample_row["tanks"]

    boilings = [make_boiling(boiling_model) for _ in range(n_tanks)]

    m.row(boilings[0], push_func=add_push)

    for b_prev, b in iter_pairs(boilings):
        m.row(b, push_func=add_push, x=b_prev["delay"].x)

    return m.root


def make_boiling_group(boiling_group_df):
    first_row = sample_row = boiling_group_df.iloc[0]

    boiling_model = delistify(sample_row["sku"].made_from_boilings, single=True)

    m = BlockMaker(
        "boiling_group",
        skus=boiling_group_df["sku"].tolist(),
        boiling_id=sample_row["absolute_batch_id"],
        boiling_model=boiling_model,
        n_tanks=sample_row["tanks"],
        group_tanks=sample_row["group_tanks"],
        first_tank=sample_row["first_tank"],
    )

    boiling_sequence = make_boiling_sequence(boiling_group_df)

    m.block(boiling_sequence)

    with code("make_analysis"):
        for boiling_pack in crop_to_chunks(boiling_sequence["boiling", True], 2, is_tail_appended=True):
            _last_boiling = boiling_pack[-1]
            analysis_start = _last_boiling["abandon"].x[0]
            with m.row("analysis_group", push_func=add_push, x=analysis_start):
                analysis = delistify(boiling_model.analysis, single=True)

                if boiling_model.flavoring_agent:
                    m.row("analysis", size=analysis.analysis_time // 5)
                    m.row("preparation", size=analysis.preparation_time // 5)
                    m.row("pumping", size=analysis.pumping_time // 5)
                else:
                    m.row("preparation", size=analysis.preparation_time // 5)
                    m.row("analysis", size=analysis.analysis_time // 5)
                    m.row("pumping", size=analysis.pumping_time // 5)

    with code("make_packing"):
        if first_row["sku"].weight_netto != 0.5:
            packing_start = m.root["analysis_group", True][0]["pumping"].x[0] + 1
        else:
            packing_start = m.root["analysis_group", True][0]["pumping"].y[0] - 1

        packing_time = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in boiling_group_df.iterrows()])
        packing_time = int(custom_round(packing_time, 5, "ceil", pre_round_precision=1))
        assert packing_time >= 15, "Время паковки должно превышать 15 минут"

        m.row("packing", push_func=add_push, x=packing_start, size=packing_time // 5)
    return m.root
