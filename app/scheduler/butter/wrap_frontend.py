from datetime import datetime
from typing import Optional

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push, simple_push
from utils_ak.block_tree.validation import disjoint_validator
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.iteration.simple_iterator import iter_pairs
from utils_ak.numeric.numeric import custom_round

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.butter.make_schedule.make_schedule import make_schedule
from app.scheduler.butter.to_boiling_plan import BoilingPlanLike
from app.scheduler.time_utils import cast_time
from app.scheduler.wrap_header import wrap_header


def _wrap_boiling_lines(schedule):
    m = BlockMaker(
        "line",
        default_row_width=1,
        default_col_width=1,
        # props
        font_size=9,
        axis=1,
    )

    with code("Init lines"):
        boiling_lines = []
        boiling_line = m.block("boiling_line_1", size=(0, 2)).block
        boiling_lines.append(boiling_line)
        boiling_line = m.block("boiling_line_2", size=(0, 2)).block
        boiling_lines.append(boiling_line)
        # m.row("stub", size=0, boiling_line=boiling_line) # create  reference for upper boiling line in stub

    for child in schedule.iter(cls=lambda cls: cls in ["preparation", "displacement", "cleaning"]):
        if not child.is_leaf():
            continue
        block = _wrap_child(child).children[0]
        push(
            boiling_lines[0],
            block,
            push_func=simple_push,
            validator=disjoint_validator,
        )

    for child in schedule.iter(cls=lambda cls: cls == "boiling"):
        block = _wrap_boiling(child)

        for i in range(len(boiling_lines)):
            push(
                boiling_lines[child.props["tank_number"]],
                block,
                push_func=add_push,
            )
    return m.root


def _wrap_child(child):
    m = BlockMaker(
        "butter_block",
        default_row_width=1,
        default_col_width=2,
        # props
        axis=0,
        tank_number=child.props.get("tank_number"),
    )

    child.update_size(size=(child.size[0], 2))

    if child.props["cls"] == "pasteurization":
        with m.block(
            "pasteurization",
            push_func=add_push,
            x=(child.x[0], 0),
            boiling_model=child.props["boiling_model"],
        ):
            m.block("pasteurization_1", push_func=add_push, size=(child.size[0], 1), x=(0, 0))
            m.block("pasteurization_2", push_func=add_push, size=(child.size[0], 1), x=(0, 1))
    else:
        m.row(m.copy(child, with_props=True), push_func=add_push)

    return m.root


def _wrap_boiling(boiling):
    m = BlockMaker(
        "boiling",
        default_row_width=1,
        default_col_width=2,
        # props
        axis=0,
    )

    for child in boiling.iter():
        child.update_size(size=(child.size[0], 2))

        if child.props["cls"] == "pasteurization":
            with m.block(
                "pasteurization", push_func=add_push, x=(child.x[0], 0), boiling_model=child.props["boiling_model"]
            ):
                m.block("pasteurization_1", push_func=add_push, size=(child.size[0], 1), x=(0, 0))

                m.block("pasteurization_2", push_func=add_push, size=(child.size[0], 1), x=(0, 1))
        else:
            m.row(m.copy(child, with_props=True), push_func=add_push)

    return m.root


def _wrap_packing(schedule):
    m = BlockMaker(
        "line",
        default_row_width=1,
        default_col_width=1,
        # props
        font_size=9,
    )
    for child_prev, child in iter_pairs(list(schedule.iter(cls="packing")), method="any_prefix"):
        child.update_size(size=(child.size[0], 2))
        if child_prev:
            m.block("cooling", size=(4, 2), x=(child.x[0] - 4, 0), push_func=add_push)

        m.row(m.copy(child, with_props=True), push_func=add_push)
    return m.root


def wrap_frontend(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"butter": 1},
    date: Optional[datetime] = None,
):
    # - Get schedule

    output = make_schedule(
        boiling_plan,
        start_time=start_time,
        first_batch_ids_by_type=first_batch_ids_by_type,
    )
    schedule = output["schedule"]

    # - Wrap schedule

    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1

    # calc start time
    start_t = int(custom_round(schedule.x[0], 12, "floor"))  # round to last hour
    start_time = cast_time(start_t)

    m.block(wrap_header(date=date, start_time=start_time, header="График работы маслоцеха"))

    with m.block(start_time=start_time, axis=1):
        m.block(_wrap_boiling_lines(schedule))

    with m.block(start_time=start_time, axis=1):
        m.block(_wrap_packing(schedule))

    # - Return

    output["frontend"] = m.root

    return output


def test():
    print(
        wrap_frontend(
            str(get_repo_path() / "app/data/static/samples/by_department/butter/2023-09-03 План по варкам масло.xlsx")
        )["frontend"]
    )


if __name__ == "__main__":
    test()
