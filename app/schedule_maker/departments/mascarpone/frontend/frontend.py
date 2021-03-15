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


def make_mascarpone_lines(schedule):
    maker, make = init_block_maker("mascarpone_lines", axis=1)

    boiling_lines = []
    for i in range(4):
        boiling_lines.append(
            make(f"boiling_line_{i}", size=(0, 2), is_parent_node=True).block
        )
        make("stub", size=(0, 1))

    for mbg in listify(schedule["mascarpone_boiling_group"]):
        line_nums = mbg.props["line_nums"]

        for i, boiling in enumerate(listify(mbg["boiling"])):
            frontend_boiling = make_frontend_mascarpone_boiling(
                boiling["boiling_process"]
            )
            push(boiling_lines[line_nums[i]], frontend_boiling, push_func=add_push)

    return maker.root


def make_cream_cheese_lines(schedule, boiling_lines=None):
    maker, make = init_block_maker("cream_cheese_lines", axis=1)

    if not boiling_lines:
        boiling_lines = []
        for i in range(3):
            boiling_lines.append(
                make(f"boiling_line_{i}", size=(0, 2), is_parent_node=True).block
            )
            make("stub", size=(0, 1))

    for i, ccb in enumerate(list(schedule.iter(cls="cream_cheese_boiling"))):
        boiling_line = boiling_lines[i % 3]
        block = make_frontend_cream_cheese_boiling(ccb)
        push(boiling_line, block, push_func=add_push)
    return maker.root


def make_packing_line(schedule):
    maker, make = init_block_maker("packing_line", axis=1)

    for mbg in listify(schedule["mascarpone_boiling_group"]):
        p1, p2 = [b["packing_process"] for b in mbg["boiling"]]
        batch_id = int(p1.props["boiling_id"]) // 2
        make(
            "packing_num",
            size=(2, 1),
            x=(p1["N"].x[0] + 1, 1),
            batch_id=batch_id,
            push_func=add_push,
        )
        for p in [p1, p2]:
            make(
                "packing",
                size=(p["packing"].size[0], 1),
                x=(p["packing"].x[0], 1),
                push_func=add_push,
            )
            make("N", size=(p["N"].size[0], 1), x=(p["N"].x[0], 0), push_func=add_push)
            make("P", size=(p["P"].size[0], 1), x=(p["P"].x[0], 0), push_func=add_push)

    return maker.root


def make_frontend_cream_cheese_boiling(boiling):
    maker, make = init_block_maker(
        "cream_cheese_boiling",
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        boiling_id=boiling.props["boiling_id"],
    )

    bp = boiling["boiling_process"]
    pp = boiling["packing_process"]

    with make():
        make("cooling", size=(bp["cooling"].size[0], 1))
        make("separation", size=(bp["separation"][0].size[0], 1))
        make("salting", size=(bp["salting"][0].size[0], 1))
        make("separation", size=(bp["separation"][1].size[0], 1))
        make("salting", size=(bp["salting"][1].size[0], 1))
        make("P", size=(bp["P"].size[0], 1))

    with make():
        make("cream_cheese_boiling_label1", size=(bp["cooling"].size[0], 1))
        make("cream_cheese_boiling_label2", size=(bp["separation"][0].size[0], 1))
        make("stub", size=(2, 1))
        make("P", size=(pp["P"].size[0], 1))
        make("packing", size=(pp["packing"].size[0], 1))

    return maker.root


def make_cleanings_line(schedule):
    maker, make = init_block_maker("cleaning_line")

    for cleaning in listify(schedule["cleaning"]):
        make(
            cleaning.children[0].props["cls"],
            size=(cleaning.size[0], 2),
            x=cleaning.x,
            push_func=add_push,
        )
    return maker.root


def make_frontend(schedule):
    maker, make = init_block_maker("frontend", axis=1)
    make("stub", size=(0, 1))  # start with 1
    make(make_mascarpone_lines(schedule))
    make(make_packing_line(schedule))
    make("stub", size=(0, 1))
    make(make_cream_cheese_lines(schedule))
    make("stub", size=(0, 1))
    make(make_cleanings_line(schedule))
    #
    # from app.schedule_maker.models import cast_model, CreamCheeseSKU
    # from app.schedule_maker.departments.mascarpone.algo.cream_cheese_boilings import (
    #     make_cream_cheese_boiling,
    # )
    #
    # # todo: del, test
    # sku = cast_model(CreamCheeseSKU, 93)
    # values = [[0, sku, 10]]
    # boiling_group_df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    # boiling = make_cream_cheese_boiling(boiling_group_df)
    # make(make_frontend_cream_cheese_boiling(boiling))
    return maker.root
