from datetime import datetime
from typing import Optional

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.time_utils import cast_time
from app.scheduler.common.wrap_header import wrap_header
from app.scheduler.ricotta.make_schedule.make_schedule import make_schedule


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
        default_column_width=1,
        # props
        axis=1,
        line=line,
    )

    # calc start time
    start_time = cast_time(start_time)

    # - Add header

    m.push(wrap_header(date=date, start_time=start_time, header="График работы рикотты"))

    # - Add shifts

    with m.push("shift_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="shift", team="Бригадир"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add shifts

    with m.push("shift_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="shift", team="Упаковка"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Boilings

    # -- Floculators

    for i in range(3):
        with m.push(f"floculator_{i + 1}", start_time=start_time, size=(0, 2)):
            for boiling in schedule.iter(cls="boiling", floculator_num=i + 1):
                with m.push("first_row", size=(0, 1), x=(0, 0), push_func=add_push):
                    m.row(m.copy(boiling["boiling_preparation"], with_props=True, size=(2, 1)), push_func=add_push)
                    m.row(m.copy(boiling["pouring"], with_props=True, size=(None, 1)), push_func=add_push)
                with m.push("second_row", size=(0, 1), x=(0, 1), push_func=add_push):
                    m.row(m.copy(boiling["heating"], with_props=True, size=(None, 1)), push_func=add_push)
                    m.row(m.copy(boiling["lactic_acid"], with_props=True, size=(None, 1)), push_func=add_push)
                    m.row(m.copy(boiling["heating_short"], with_props=True, size=(None, 1)), push_func=add_push)
                    m.row(m.copy(boiling["draw_whey"], with_props=True, size=(None, 1)), push_func=add_push)

    # -- Drenators

    for i in range(2):
        with m.push(f"drenator_{i + 1}", start_time=start_time, size=(0, 1)):
            for block in schedule.iter(
                cls=lambda cls: cls in ["dray_ricotta", "salting", "ingredient", "manual_cleaning"], drenator_num=i + 1
            ):
                m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # -- Pumping

    with m.push("pumping_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="pumping"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # -- Packing

    with m.push("packing_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="packing"):
            m.push(
                "packing_header",
                size=(2, 1),
                x=(block.x[0], 0),
                absolute_batch_id=block.props["absolute_batch_id"],
                push_func=add_push,
            )
            m.row(m.copy(block, with_props=True, size=(block.size[0] - 2, 1)), x=block.x[0] + 2, push_func=add_push)

    # - Cleaning

    with m.push("cleaning_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="cleaning"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add preparation

    m.push(m.copy(schedule["preparation"], with_props=True), size=(6, 13), x=(0, 1), push_func=add_push)

    # - Add template

    with m.push("template_block", index_width=1, push_func=add_push):
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
                ("Ильпра линейная", 1),
                ("Сип-мойка контур 2", 1),
            ]
        ):
            m.push(
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
        default_column_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1

    m.push(wrap_line(schedule, line="Кремчиз", date=date, start_time=start_time))

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
