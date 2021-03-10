from utils_ak.block_tree import *
from utils_ak.iteration import *
from utils_ak.builtin import *

from app.schedule_maker.models import *


def make_boiling(boiling_model):
    maker, make = init_block_maker("boiling", boiling_label="рикотта")

    bt = boiling_model.boiling_technology
    make("heating", size=(bt.heating_time // 5, 0))
    make("delay", size=(bt.delay_time // 5, 0))
    make("protein_harvest", size=(bt.protein_harvest_time // 5, 0))
    make("abandon", size=(bt.abandon_time // 5, 0))
    make("pumping_out", size=(bt.pumping_out_time // 5, 0))

    return maker.root


def make_boiling_sequence(boiling_group_df):
    maker, make = init_block_maker("boiling_sequence")

    # check that only one boiling model is present in boiling_group_df
    assert (
        len(
            set(
                sum(
                    [
                        row["sku"].made_from_boilings
                        for i, row in boiling_group_df.iterrows()
                    ],
                    [],
                )
            )
        )
        == 1
    ), "В одной из групп варок возможно использование сразу нескольких типов варок."
    boiling_model = boiling_group_df.iloc[0]["sku"].made_from_boilings[0]

    boilings = [make_boiling(boiling_model) for _ in range(len(boiling_group_df))]

    for b_prev, b in SimpleIterator(boilings).iter_sequences(2, method="any"):
        if not b:
            continue

        if not b_prev:
            push(maker.root, b, push_func=add_push)
        else:
            b.props.update(x=(b_prev["delay"].x[0], 0))
            push(maker.root, b, push_func=add_push)
    return maker.root


def make_boiling_group(boiling_group_df):
    maker, make = init_block_maker(
        "boiling_group",
        skus=boiling_group_df["sku"].tolist(),
        boiling_id=boiling_group_df.iloc[0]["boiling_id"],
    )
    boiling_sequence = make_boiling_sequence(boiling_group_df)
    push(maker.root, boiling_sequence)
    analysis_start = listify(boiling_sequence["boiling"])[-1]["abandon"].x[0]
    with make("analysis_group", x=(analysis_start, 0), push_func=add_push):
        analysis = cast_model(
            RicottaAnalysisTechnology, 1
        )  # todo: take from boiling_model
        make("preparation", size=(analysis.preparation_time // 5, 0))
        make("analysis", size=(analysis.preparation_time // 5, 0))
        make("pumping", size=(analysis.preparation_time // 5, 0))

    packing_start = maker.root["analysis_group"]["pumping"].x[0] + 1

    # todo: pauses
    packing_time = sum(
        [
            row["kg"] / row["sku"].packing_speed * 60
            for i, row in boiling_group_df.iterrows()
        ]
    )
    packing_time = int(custom_round(packing_time, 5, "ceil"))

    make(
        "packing", x=(packing_start, 0), size=(packing_time // 5, 0), push_func=add_push
    )
    return maker.root
