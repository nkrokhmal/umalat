import copy

from datetime import datetime
from typing import Optional

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.filter_block import filter_block
from utils_ak.block_tree.pushers.pushers import add_push, push, simple_push
from utils_ak.block_tree.validation import disjoint_validator
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.iteration.simple_iterator import iter_pairs
from utils_ak.numeric.numeric import custom_round

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.ricotta.make_schedule.make_schedule import make_schedule
from app.scheduler.time_utils import cast_time
from app.scheduler.wrap_header import wrap_header


LINE_HEIGHT = 14


def wrap_line(
    schedule,
    line: str,
    date: datetime,
    start_time="07:00",
):
    # - Init block maker

    m = BlockMaker(
        "line",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
        line=line,
    )

    # calc start time
    start_time = cast_time(start_time)

    # - Add header

    m.block(wrap_header(date=date, start_time=start_time, header="График работы рикотты"))

    # - Add shifts

    with m.block("shift_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="shift", team="Бригадир"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add shifts

    with m.block("shift_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="shift", team="Упаковка"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Boilings

    # -- Floculators

    for i in range(3):
        with m.block(f"floculator_{i + 1}", start_time=start_time, size=(0, 2)):
            for floculator in schedule.iter(cls="floculator", floculator_num=i + 1):
                with m.block("first_row", size=(0, 1), x=(0, 0), push_func=add_push):
                    m.row(m.copy(floculator["boiling_preparation"], with_props=True, size=(2, 1)), push_func=add_push)
                    m.row(m.copy(floculator["pouring"], with_props=True, size=(None, 1)), push_func=add_push)
                with m.block("second_row", size=(0, 1), x=(0, 1), push_func=add_push):
                    m.row(m.copy(floculator["heating"], with_props=True, size=(None, 1)), push_func=add_push)
                    m.row(m.copy(floculator["lactic_acid"], with_props=True, size=(None, 1)), push_func=add_push)
                    m.row(m.copy(floculator["draw_whey"], with_props=True, size=(None, 1)), push_func=add_push)

    # -- Drenators

    for i in range(2):
        with m.block(f"drenator_{i + 1}", start_time=start_time, size=(0, 1)):
            for block in schedule.iter(cls=lambda cls: cls in ["dray_ricotta", "salting"], drenator_num=i + 1):
                m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # -- Pumping

    with m.block("pumping_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="pumping"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # -- Packing

    with m.block("packing_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="packing"):
            m.block(
                "packing_header",
                size=(2, 1),
                x=(block.x[0], 0),
                absolute_batch_id=block.props["absolute_batch_id"],
                push_func=add_push,
            )
            m.row(m.copy(block, with_props=True, size=(block.size[0] - 2, 1)), x=block.x[0] + 2, push_func=add_push)

    # - Cleaning

    with m.block("cleaning_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="cleaning"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add preparation

    m.block(m.copy(schedule["preparation"], with_props=True), size=(6, 13), x=(0, 1), push_func=add_push)

    # - Add template

    with m.block("template_block", index_width=1, push_func=add_push):
        current_row = 1
        for i, (row_name, size) in enumerate(
            [
                ("Бригадир", 1),
                ("Упаковка", 1),
                ("Флокулятор №1", 2),
                ("Флокулятор №2", 2),
                ("Флокулятор №3", 2),
                ("Дренатор/Бак 1", 1),
                ("Дренатор/Бак 2", 1),
                ("Перекачивание в буферный танк", 1),
                ("Упаковка на Ильпре", 1),
                ("Сип-мойка контур 2", 1),
            ]
        ):
            m.block(
                "template",
                push_func=add_push,
                x=(1, current_row),
                size=(2, size),
                text=row_name,
            )
            current_row += size

    return m.root


def wrap_frontend(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"ricotta": 1},
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

    m.block(wrap_line(schedule, line="Кремчиз", date=date, start_time=start_time))

    # - Return

    output["frontend"] = m.root

    return output


def test():
    print(
        wrap_frontend(
            str(get_repo_path() / "app/data/tests/ricotta/boiling.xlsx"),
        )["frontend"]
    )


if __name__ == "__main__":
    test()
