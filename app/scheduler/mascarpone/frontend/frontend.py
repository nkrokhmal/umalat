from app.imports.runtime import *
from app.scheduler.time import *


def make_frontend_mascarpone_boiling(boiling_process):
    is_cream = boiling_process.props["boiling_group_dfs"][0].iloc[0]["is_cream"]

    maker, make = utils.init_block_maker(
        "boiling",
        axis=1,
        x=(boiling_process.x[0], 0),
        size=(0, 2),
        batch_id=boiling_process.props["boiling_group_dfs"][0].iloc[0]["batch_id"],
        is_cream=is_cream,
    )

    with make():
        make("boiling_num", size=(3, 1))
        make(
            "boiling_name",
            size=(boiling_process.size[0] - 3, 1),
            boiling_volume=boiling_process.props["boiling_volume"],
            n=boiling_process.props["n"],
        )

    with make():
        make("pouring", size=(boiling_process["pouring"].size[0], 1))
        make("heating", size=(boiling_process["heating"].size[0], 1))
        if boiling_process["waiting"].size[0]:
            make("waiting", size=(boiling_process["waiting"].size[0], 1))
        make(
            "adding_lactic_acid",
            size=(boiling_process["adding_lactic_acid"].size[0], 1),
        )
        make(
            "pumping_off",
            size=(boiling_process["pumping_off"].size[0], 1),
        )
    return maker.root


def make_mascarpone_lines(schedule, with_cream_cheese=False):

    maker, make = utils.init_block_maker("mascarpone_lines", axis=1)

    boiling_lines = []
    for i in range(4):
        boiling_lines.append(
            make(f"boiling_line_{i}", size=(0, 2)).block
        )
        make("stub", size=(0, 1))

    # non-cream
    for mbg in schedule.iter(
        cls="mascarpone_boiling_group",
        boiling_group_dfs=lambda dfs: not dfs[0].iloc[0]["is_cream"],
    ):
        line_nums = mbg.props["line_nums"]

        for i, boiling in enumerate(mbg["boiling", True]):
            frontend_boiling = make_frontend_mascarpone_boiling(
                boiling["boiling_process"]
            )
            utils.push(
                boiling_lines[line_nums[i] - 1],
                frontend_boiling,
                push_func=utils.add_push,
            )

    # cream
    cycle = itertools.cycle(boiling_lines)
    for mbg in schedule.iter(
        cls="mascarpone_boiling_group",
        boiling_group_dfs=lambda dfs: dfs[0].iloc[0]["is_cream"],
    ):
        for i, boiling in enumerate(mbg["boiling", True]):
            block = make_frontend_mascarpone_boiling(boiling["boiling_process"])
            for i in range(len(boiling_lines)):
                boiling_line = next(cycle)
                try:
                    res = utils.push(
                        boiling_line,
                        block,
                        push_func=utils.simple_push,
                        validator=utils.disjoint_validator,
                    )
                    assert isinstance(res, utils.Block)
                except:
                    if i == len(boiling_lines) - 1:
                        # create new line
                        boiling_lines.append(
                            make(
                                f"boiling_line_{i}", size=(0, 2)
                            ).block
                        )
                        make("stub", size=(0, 1))
                        utils.push(
                            boiling_lines[-1],
                            block,
                            push_func=utils.simple_push,
                            validator=utils.disjoint_validator,
                        )
                        cycle = itertools.cycle(boiling_lines)

                    else:
                        continue
                break

    if with_cream_cheese:
        cycle = itertools.cycle(boiling_lines)
        for i, ccb in enumerate(list(schedule.iter(cls="cream_cheese_boiling"))):
            block = make_frontend_cream_cheese_boiling(ccb)

            for i in range(len(boiling_lines)):
                boiling_line = next(cycle)
                try:
                    res = utils.push(
                        boiling_line,
                        block,
                        push_func=utils.simple_push,
                        validator=utils.disjoint_validator,
                    )

                    assert isinstance(res, utils.Block)
                except:
                    if i == len(boiling_lines) - 1:
                        # create new line
                        # print("Creating new line")
                        boiling_lines.append(
                            make(
                                f"boiling_line_{i}", size=(0, 2)
                            ).block
                        )
                        make("stub", size=(0, 1))
                        utils.push(
                            boiling_lines[-1],
                            block,
                            push_func=utils.simple_push,
                            validator=utils.disjoint_validator,
                        )
                        cycle = itertools.cycle(boiling_lines)
                    else:
                        # go for next try
                        continue

                break

    return maker.root


def make_cream_cheese_lines(schedule, boiling_lines=None):
    maker, make = utils.init_block_maker("cream_cheese_lines", axis=1)

    if not boiling_lines:
        boiling_lines = []
        for i in range(3):
            boiling_lines.append(
                make(f"boiling_line_{i}", size=(0, 2)).block
            )
            make("stub", size=(0, 1))

    for i, ccb in enumerate(list(schedule.iter(cls="cream_cheese_boiling"))):
        boiling_line = boiling_lines[i % 3]
        block = make_frontend_cream_cheese_boiling(ccb)
        utils.push(boiling_line, block, push_func=utils.add_push)
    return maker.root


def make_packing_line(schedule):
    maker, make = utils.init_block_maker("packing_line", axis=1)

    if "mascarpone_boiling_group" not in [c.props["cls"] for c in schedule.children]:
        return

    for mbg in schedule["mascarpone_boiling_group", True]:
        packing_processes = [
            b["packing_process"] for b in mbg["boiling", True]
        ]

        make(
            "packing_num",
            size=(2, 1),
            x=(
                packing_processes[0]["packing_group"]["P", True][0].x[0] - 1,
                1,
            ),
            batch_id=mbg.props["boiling_group_dfs"][0].iloc[0]["batch_id"],
            push_func=utils.add_push,
        )
        for p in packing_processes:
            for block in p.iter(cls=lambda cls: cls in ["N", "ingredient", "P"]):
                make(
                    block.props["cls"],
                    size=(block.size[0], 1),
                    x=(block.x[0], 0),
                    push_func=utils.add_push,
                )
            for block in p.iter(cls="packing"):
                make(
                    "packing",
                    size=(block.size[0], 1),
                    x=(block.x[0], 1),
                    push_func=utils.add_push,
                )

    return maker.root


def make_frontend_cream_cheese_boiling(boiling):
    maker, make = utils.init_block_maker(
        "cream_cheese_boiling",
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        batch_id=boiling.props["boiling_plan_df"].iloc[0]["batch_id"],
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
        make(
            "cream_cheese_boiling_label1",
            size=(bp["cooling"].size[0], 1),
            sourdoughs=boiling.props["sourdoughs"],
        )
        make("cream_cheese_boiling_label2", size=(bp["separation"][0].size[0], 1))
        make("stub", size=(2, 1))
        make("P", size=(pp["P"].size[0], 1))
        make("packing", size=(pp["packing"].size[0], 1))

    return maker.root


def make_cleanings_line(schedule):
    maker, make = utils.init_block_maker("cleaning_line")

    for cleaning in schedule.iter(cls="cleaning"):
        make(
            cleaning.children[0].props["cls"],
            size=(cleaning.size[0], 2),
            x=cleaning.x,
            push_func=utils.add_push,
            sourdoughs=cleaning.props.get("sourdoughs"),
        )
    return maker.root


def make_header(date, start_time="07:00"):
    maker, make = utils.init_block_maker("header", axis=1)

    with make("header", size=(0, 1), index_width=2):
        make(size=(1, 1), text="График наливов сыворотки")
        make(size=(1, 1), text=utils.cast_str(date, "%d.%m.%Y"), bold=True)
        for i in range(566):
            cur_time = cast_time(i + cast_t(start_time))
            days, hours, minutes = cur_time.split(":")
            if cur_time[-2:] == "00":
                make(
                    size=(1, 1),
                    text=str(int(hours)),
                    color=(218, 150, 148),
                    text_rotation=90,
                    font_size=9,
                )
            else:
                make(
                    size=(1, 1),
                    text=minutes,
                    color=(204, 255, 255),
                    text_rotation=90,
                    font_size=9,
                )
    return maker.root["header"]


def make_frontend(schedule, date=None, start_time="07:00"):
    date = date or datetime.now()

    maker, make = utils.init_block_maker("frontend", axis=1)
    make("stub", size=(0, 1))  # start with 1
    make(make_header(date=date, start_time=start_time))

    with make(x=(6, 2), push_func=utils.add_push, axis=1):
        make(make_mascarpone_lines(schedule, with_cream_cheese=True))
        make(make_packing_line(schedule))
        make("stub", size=(0, 1))
        # make(make_cream_cheese_lines(schedule))
        # make("stub", size=(0, 1))
        make(make_cleanings_line(schedule))
        make(
            "mascarpone_department_preparation",
            size=(6, 11),
            x=(-6, 0),
            push_func=utils.add_push,
        )
    #
    # from app.schedule_maker.models import cast_model, CreamCheeseSKU
    # from app.schedule_maker.mascarpone.algo.cream_cheese_boilings import (
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
