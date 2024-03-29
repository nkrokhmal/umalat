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
from app.scheduler.mascarpone.make_schedule.make_schedule import make_schedule
from app.scheduler.mascarpone.to_boiling_plan import BoilingPlanLike
from app.scheduler.time_utils import cast_time
from app.scheduler.wrap_header import wrap_header


LINE_HEIGHT = 14


def wrap_line(schedule, line: str, date: datetime, start_time="07:00"):
    # - Copy schedule

    schedule = copy.deepcopy(schedule)

    # - Filter line

    schedule = filter_block(block=schedule, cond=lambda b: b.props["line"] == line)

    if not schedule:
        return

    # - Init block maker

    m = BlockMaker(
        "line",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
        line=line,
    )
    m.row("stub", size=0)  # start with 1

    # calc start time
    start_time = cast_time(start_time)

    # - Add header

    m.block(wrap_header(date=date, start_time=start_time, header="График работы маскарпоне"))

    # - Add shifts

    with m.block("shift_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="shift", team="Бригадир"):
            m.row(m.copy(block, with_props=True, size=(None, 1)), push_func=add_push)

    # - Add shifts

    with m.block("shift_line", start_time=start_time, size=(0, 1)):
        for block in schedule.iter(cls="shift", team="Упаковка"):
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
        for block in schedule.iter(cls=lambda cls: cls in ["analysis", "ingredient", "packing", "packing_switch"]):
            if not block.props["disabled"]:
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

    m.block(
        "preparation",
        x=(next(schedule.iter(cls="preparation")).x[0], 4),
        start_time=start_time,
        size=(6, 10),
        push_func=add_push,
    )

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
            text="Грюнвальд" if line == 1 else "Ильпра роторная",
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

    return m.root


def wrap_frontend(
    boiling_plan: BoilingPlanLike,
    start_times_by_line: dict = {"Маскарпоне": "07:00", "Кремчиз": "08:00"},
    first_batch_ids_by_type: dict = {"cottage_cheese": 1, "cream": 1, "mascarpone": 1, "cream_cheese": 1},
    date: Optional[datetime] = None,
    add_cleaning_after_eight_mascarpone_boilings: bool = False,
):
    # - Get schedule

    output = make_schedule(
        boiling_plan,
        start_times_by_line=start_times_by_line,
        first_batch_ids_by_type=first_batch_ids_by_type,
        add_cleaning_after_eight_mascarpone_boilings=add_cleaning_after_eight_mascarpone_boilings,
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

    m.block(wrap_line(schedule, line="Кремчиз", date=date, start_time=min(start_times_by_line.values())))
    m.block(wrap_line(schedule, line="Маскарпоне", date=date, start_time=min(start_times_by_line.values())))

    # - Return

    output["frontend"] = m.root

    return output


def test():
    print(
        wrap_frontend(str(get_repo_path() / "app/data/static/samples/by_department/mascarpone/План по варкам.xlsx"))[
            "frontend"
        ]
    )


if __name__ == "__main__":
    test()
