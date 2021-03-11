from utils_ak.block_tree import *
from utils_ak.builtin import *


def make_frontend_mascarpone_boiling(boiling_process):
    maker, make = init_block_maker(
        "boiling",
        axis=1,
        x=(boiling_process.x[0], 0),
        size=(0, 2),
        boiling_id=boiling_process.props["boiling_id"],
    )
    with make():
        make("boiling_num", size=(3, 1))
        make("boiling_name", size=(boiling_process.size[0] - 3, 1))

    with make():
        make("pouring", size=(boiling_process["pouring"].size[0], 1))
        make("heating", size=(boiling_process["heating"].size[0], 1))
        if boiling_process["waiting"].size[0]:
            make("waiting", size=(boiling_process["waiting"].size[0], 1))
        make(
            "adding_lactic_acid",
            size=(boiling_process["adding_lactic_acid"].size[0], 1),
        )
        make("separation", size=(boiling_process["separation"].size[0], 1))
    return maker.root


def make_frontend(schedule):
    maker, make = init_block_maker("frontend", axis=1)
    make("stub", size=(0, 1))  # start with 1
    make(
        make_frontend_mascarpone_boiling(
            schedule["mascarpone_boiling_group"][0]["boiling"][0]["boiling_process"]
        )
    )
    return maker.root
