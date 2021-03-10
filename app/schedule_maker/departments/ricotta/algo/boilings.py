from utils_ak.block_tree import *
from utils_ak.iteration import *
from utils_ak.builtin import *

from app.schedule_maker.models import *


def make_boiling(boiling_model):
    maker, make = init_block_maker(
        "boiling", boiling_id=1, boiling_label="рикотта"
    )  # todo: set boiling_id from inputs

    bt = boiling_model.boiling_technology
    make("heating", size=(bt.heating_time // 5, 0))
    make("delay", size=(bt.delay_time // 5, 0))
    make("protein_harvest", size=(bt.protein_harvest_time // 5, 0))
    make("abandon", size=(bt.abandon_time // 5, 0))
    make("pumping_out", size=(bt.pumping_out_time // 5, 0))

    return maker.root


def make_boiling_sequence(sku):
    boiling_model = sku.made_from_boilings[0]
    maker, make = init_block_maker("boiling_sequence")
    n_boilings = 3  # todo: take from sku
    boilings = [make_boiling(boiling_model) for _ in range(n_boilings)]

    for b_prev, b in SimpleIterator(boilings).iter_sequences(2, method="any"):
        if not b:
            continue

        if not b_prev:
            push(maker.root, b, push_func=add_push)
        else:
            b.props.update(x=(b_prev["delay"].x[0], 0))
            push(maker.root, b, push_func=add_push)
    return maker.root


def make_boiling_group(sku):
    kg = 50  # todo: rake from input
    maker, make = init_block_maker("boiling_group")
    boiling_sequence = make_boiling_sequence(sku)
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
    packing_time = custom_round(kg / sku.packing_speed * 60, 5, "ceil")

    make(
        "packing", x=(packing_start, 0), size=(packing_time // 5, 0), push_func=add_push
    )
    return maker.root
