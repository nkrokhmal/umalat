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


def make_boiling_lines(schedule):
    maker, make = init_block_maker("boiling_lines", axis=1)

    boiling_lines = []
    for i in range(4):
        boiling_lines.append(
            make(f"boiling_line_{i}", size=(0, 2), is_parent_node=True).block
        )
        make("stub", size=(0, 1))

    for mascarpone_boiling_group in listify(schedule["mascarpone_boiling_group"]):
        line_nums = mascarpone_boiling_group.props["line_nums"]

        for i, boiling in enumerate(listify(mascarpone_boiling_group["boiling"])):
            frontend_boiling = make_frontend_mascarpone_boiling(
                boiling["boiling_process"]
            )
            push(boiling_lines[line_nums[i]], frontend_boiling, push_func=add_push)
    return maker.root


def make_frontend(schedule):
    maker, make = init_block_maker("frontend", axis=1)
    make("stub", size=(0, 1))  # start with 1
    make(make_boiling_lines(schedule))
    return maker.root
