# fmt: off
from app.imports.runtime import *
from app.scheduler.time import *

from app.scheduler.header import wrap_header

from utils_ak.block_tree import *


def wrap_frontend_mascarpone_boiling(boiling_process):
    is_cream = boiling_process.props["boiling_group_dfs"][0].iloc[0]["is_cream"]

    m = BlockMaker(
        "boiling",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
        x=(boiling_process.x[0], 0),
        size=(0, 2),
        batch_id=boiling_process.props["boiling_group_dfs"][0].iloc[0]["batch_id"],
        is_cream=is_cream,
    )

    with m.block():
        m.row("boiling_num", size=3)
        m.row(
            "boiling_name",
            size=boiling_process.size[0] - 3,
            boiling_volume=boiling_process.props["boiling_volume"],
            n=boiling_process.props["n"],
        )

    with m.block():
        m.row("pouring", size=boiling_process["pouring"].size[0])
        m.row("heating", size=boiling_process["heating"].size[0])
        if boiling_process["waiting"].size[0]:
            m.row("waiting", size=boiling_process["waiting"].size[0])
        m.row("adding_lactic_acid", size=boiling_process["adding_lactic_acid"].size[0])
        m.row("pumping_off", size=boiling_process["pumping_off"].size[0])
    return m.root


def wrap_mascarpone_lines(schedule, with_cream_cheese=False):

    m = BlockMaker("mascarpone_lines",
                   default_row_width=1,
                   default_col_width=1,
                   # props
                   axis=1)

    with code('Init lines'):
        boiling_lines = []
        for i in range(4):
            boiling_lines.append(m.block(f"boiling_line_{i}", size=(0, 2)).block)
            m.row("stub", size=0)

    with code('Make mascarpone'):
        for mbg in schedule.iter(
            cls="mascarpone_boiling_group",
            boiling_group_dfs=lambda dfs: not dfs[0].iloc[0]["is_cream"],
        ):
            line_nums = mbg.props["line_nums"]

            for i, boiling in enumerate(mbg["boiling", True]):
                frontend_boiling = wrap_frontend_mascarpone_boiling(boiling["boiling_process"])
                push(
                    boiling_lines[line_nums[i] - 1],
                    frontend_boiling,
                    push_func=add_push,
                )

    with code('Make cream'):
        cycle = itertools.cycle(boiling_lines)
        for mbg in schedule.iter(
            cls="mascarpone_boiling_group",
            boiling_group_dfs=lambda dfs: dfs[0].iloc[0]["is_cream"],
        ):
            for i, boiling in enumerate(mbg["boiling", True]):
                block = wrap_frontend_mascarpone_boiling(boiling["boiling_process"])
                for i in range(len(boiling_lines)):
                    boiling_line = next(cycle)
                    try:
                        res = push(
                            boiling_line,
                            block,
                            push_func=simple_push,
                            validator=disjoint_validator,
                        )
                        assert isinstance(res, Block)
                    except:
                        if i == len(boiling_lines) - 1:
                            # create new line
                            boiling_lines.append(m.block(f"boiling_line_{i}", size=(0, 2)).block)
                            m.row("stub", size=0)
                            push(
                                boiling_lines[-1],
                                block,
                                push_func=simple_push,
                                validator=disjoint_validator,
                            )
                            cycle = itertools.cycle(boiling_lines)

                        else:
                            continue
                    break

    with code('Make cream cheese'):
        if with_cream_cheese:
            cycle = itertools.cycle(boiling_lines)
            for i, ccb in enumerate(list(schedule.iter(cls="cream_cheese_boiling"))):
                block = wrap_frontend_cream_cheese_boiling(ccb)

                for i in range(len(boiling_lines)):
                    boiling_line = next(cycle)
                    try:
                        res = push(
                            boiling_line,
                            block,
                            push_func=simple_push,
                            validator=disjoint_validator,
                        )

                        assert isinstance(res, Block)
                    except:
                        if i == len(boiling_lines) - 1:
                            # create new line
                            # print("Creating new line")
                            boiling_lines.append(m.block(f"boiling_line_{i}", size=(0, 2)).block)
                            m.row("stub", size=0)
                            push(
                                boiling_lines[-1],
                                block,
                                push_func=simple_push,
                                validator=disjoint_validator,
                            )
                            cycle = itertools.cycle(boiling_lines)
                        else:
                            # go for next try
                            continue

                    break

    return m.root


def wrap_cream_cheese_lines(schedule, boiling_lines=None):
    m = BlockMaker("cream_cheese_lines",
                   default_row_width=1,
                   default_col_width=1,
                   # props
                   axis=1)

    with code('Init lines'):
        if not boiling_lines:
            boiling_lines = []
            for i in range(3):
                boiling_lines.append(m.block(f"boiling_line_{i}", size=(0, 2)).block)
                m.row("stub", size=1)

    with code('Fill lines'):
        for i, ccb in enumerate(list(schedule.iter(cls="cream_cheese_boiling"))):
            boiling_line = boiling_lines[i % 3]
            block = wrap_frontend_cream_cheese_boiling(ccb)
            push(boiling_line, block, push_func=add_push)
    return m.root


def make_packing_line(schedule):
    m = BlockMaker("packing_line",
                   default_row_width=1,
                   default_col_width=1,
                   # props
                   axis=1)

    if "mascarpone_boiling_group" not in [c.props["cls"] for c in schedule.children]:
        return

    for mbg in schedule["mascarpone_boiling_group", True]:
        packing_processes = [b["packing_process"] for b in mbg["boiling", True]]

        m.row(
            "packing_num",
            size=2,
            x=(
                packing_processes[0]["packing_group"]["P", True][0].x[0] - 1,
                1,
            ),
            batch_id=mbg.props["boiling_group_dfs"][0].iloc[0]["batch_id"],
            push_func=add_push,
        )
        for p in packing_processes:
            for block in p.iter(cls=lambda cls: cls in ["N", "ingredient", "P"]):
                m.row(
                    block.props["cls"],
                    size=block.size[0],
                    x=(block.x[0], 0),
                    push_func=add_push,
                )
            for block in p.iter(cls="packing"):
                m.row(
                    "packing",
                    size=block.size[0],
                    x=(block.x[0], 1),
                    push_func=add_push,
                )

    return m.root


def wrap_frontend_cream_cheese_boiling(boiling):
    m = BlockMaker(
        "cream_cheese_boiling",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        batch_id=boiling.props["boiling_plan_df"].iloc[0]["batch_id"],
    )

    bp = boiling["boiling_process"]
    pp = boiling["packing_process"]

    with m.block():
        m.row("cooling", size=bp["cooling"].size[0])
        m.row("separation", size=bp["separation"][0].size[0])
        m.row("salting", size=bp["salting"][0].size[0])
        m.row("separation", size=bp["separation"][1].size[0])
        m.row("salting", size=bp["salting"][1].size[0])
        m.row("P", size=bp["P"].size[0])

    with m.block():
        m.row(
            "cream_cheese_boiling_label1",
            size=(bp["cooling"].size[0], 1),
            sourdoughs=boiling.props["sourdoughs"],
        )
        m.row("cream_cheese_boiling_label2", size=bp["separation"][0].size[0])
        m.row("stub", size=2)
        m.row("P", size=pp["P"].size[0])
        m.row("packing", size=pp["packing"].size[0])

    return m.root


def wrap_cleanings_line(schedule):
    m = BlockMaker("cleaning_line")

    for cleaning in schedule.iter(cls="cleaning"):
        m.block(
            cleaning.children[0].props["cls"],
            size=(cleaning.size[0], 2),
            x=cleaning.x,
            push_func=add_push,
            sourdoughs=cleaning.props.get("sourdoughs"),
        )
    return m.root


def wrap_preparation(schedule):
    m = BlockMaker('preparation')
    return m.create_block('preparation',
                   x=(schedule['preparation'].x[0], 1),
                   size=(schedule['preparation'].size[0], 11))

def wrap_shifts(shifts):
    m = BlockMaker("shifts")
    shifts = m.copy(shifts, with_props=True)
    for shift in shifts.iter(cls='shift'):
        shift.update_size(size=(shift.size[0], 1)) # todo maybe: refactor. Should be better
    m.block(shifts, push_func=add_push)
    return m.root

def wrap_frontend(schedule, date=None):
    date = date or datetime.now()

    m = BlockMaker("frontend",
                   default_row_width=1,
                   default_col_width=1,
                   # props
                   axis=1)

    m.row("stub", size=0)  # start with 1

    # calc start time
    start_t = int(utils.custom_round(schedule.x[0], 12, "floor"))  # round to last hour and add half hour
    start_time = cast_time(start_t)
    m.block(wrap_header(date=date, start_time=start_time, header="График наливов сыворотки"))
    with m.block(push_func=add_push,
                 x=(0, 2),
                 axis=1,
                 start_time=cast_time(start_t)):
        m.col(wrap_shifts(schedule['shifts']['meltings']))
        m.block(wrap_mascarpone_lines(schedule, with_cream_cheese=True))
        m.col(wrap_shifts(schedule['shifts']['packings']))
        m.block(make_packing_line(schedule))
        m.row("stub", size=0)
        m.block(wrap_cleanings_line(schedule))
        m.block(wrap_preparation(schedule), push_func=add_push)
    return m.root
