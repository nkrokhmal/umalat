from datetime import datetime
from typing import Optional

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push, simple_push
from utils_ak.block_tree.validation import disjoint_validator
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.iteration.simple_iterator import iter_pairs
from utils_ak.numeric.numeric import custom_round

from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.mascarpone.make_schedule.make_schedule import make_schedule
from app.scheduler.mascarpone.to_boiling_plan import BoilingPlanLike
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
        "mascarpone_block",
        default_row_width=1,
        default_col_width=2,
        # props
        axis=0,
        tank_number=child.props.get("tank_number"),
    )

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
    first_batch_ids_by_type: dict = {"cottage_cheese": 1, "cream": 1, "mascarpone": 1, "cream_cheese": 1},
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

    # - Init block maker

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

    # - Add header

    m.block(wrap_header(date=date, start_time=start_time, header="График работы маскарпоне"))

    # - Add shifts

    with m.block("shift_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="shift", team="brigadir"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add shifts

    with m.block("shift_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="shift", team="packer"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add boiling header

    with m.block("boiling_header_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="boiling_header"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add pouring cream line

    with m.block("pouring_cream_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="pouring_cream"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add separator

    with m.block("separator_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls=lambda cls: cls in ["separation", "separator_acceleration"]):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add бак 1

    with m.block("tub_1_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls=lambda cls: cls in ["pouring", "salting", "heating"], tub_num=1):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add бак 2

    with m.block("tub_2_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls=lambda cls: cls in ["pouring", "salting", "heating"], tub_num=2):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add pumping

    with m.block("pumping_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="pumping"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add бак 3

    with m.block("tub_3_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls=lambda cls: cls in ["analysis", "ingredient", "packing"]):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add packing lines

    with m.block("contour_0", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls=lambda cls: "cleaning", contour="0"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    with m.block("contour_1", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls=lambda cls: "cleaning", contour="1"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    with m.block("contour_2", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls=lambda cls: "cleaning", contour="2"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add preparation

    m.block("preparation", x=(0, 4), size=(6, 10), push_func=add_push)

    # - Add template

    with m.block("template_block", index_width=1, push_func=add_push):
        m.block(
            "template",
            push_func=add_push,
            x=(1, 6),
            size=(2, 1),
            text="Сепаратор",
        )
        m.block(
            "template",
            push_func=add_push,
            x=(1, 7),
            size=(2, 1),
            text="Бак 1",
        )
        m.block(
            "template",
            push_func=add_push,
            x=(1, 8),
            size=(2, 1),
            text="Бак 2",
        )
        m.block(
            "template",
            push_func=add_push,
            x=(1, 9),
            size=(2, 1),
            text="Перекачивание в фасовочный танк",
        )
        m.block(
            "template",
            push_func=add_push,
            x=(1, 10),
            size=(2, 1),
            text="Бак 3",
        )
        m.block(
            "template",
            push_func=add_push,
            x=(1, 11),
            size=(2, 1),
            text="Грюнвальд",
        )
        m.block(
            "template",
            push_func=add_push,
            x=(1, 12),
            size=(2, 1),
            text="Контур 1",
        )
        m.block(
            "template",
            push_func=add_push,
            x=(1, 13),
            size=(2, 1),
            text="Контур 2",
        )

    # - Return

    output["frontend"] = m.root

    return output


def test():
    print(wrap_frontend(str(get_repo_path() / "app/data/static/samples/by_department/mascarpone/План по варкам.xlsx")))


if __name__ == "__main__":
    test()
