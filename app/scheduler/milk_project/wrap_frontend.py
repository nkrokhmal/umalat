from datetime import datetime

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push
from utils_ak.numeric.numeric import custom_round

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.time_utils import cast_time
from app.scheduler.common.wrap_header import wrap_header
from app.scheduler.milk_project.make_schedule.make_schedule import make_schedule
from app.scheduler.milk_project.to_boiling_plan import BoilingPlanLike


def wrap_line(schedule):
    m = BlockMaker(
        "line",
        default_row_width=2,
        default_column_width=2,
        # props
        font_size=9,
    )
    for child in schedule.children:
        if child.props["cls"] == "boiling_sequence":
            for i, block in enumerate(child.children):
                if i <= 1:
                    # water collecting
                    _block = m.copy(block, with_props=True)
                    _block.update_size(size=(block.size[0], 2))
                    m.push(_block, push_func=add_push)
                else:
                    for element in block.children:
                        _element = m.copy(element, with_props=True)
                        _element.update_size(size=(element.size[0], 2))
                        _element.props.update(x=(element.x[0], (i - 2) * 2))
                        m.push(_element, push_func=add_push)
        elif child.props["cls"] == "pouring_off":
            _child = m.copy(child, with_props=True)
            _child.update_size(size=(child.size[0], 6))
            m.push(_child, push_func=add_push)
    return m.root


def wrap_frontend(
    boiling_plan: BoilingPlanLike,
    date=None,
    start_time="07:00",
    first_batch_ids_by_type={"milk_project": 1},
) -> dict:
    # - Get schedule and boiling_plan_df

    output = make_schedule(
        boiling_plan=boiling_plan,
        start_time=start_time,
        first_batch_ids_by_type=first_batch_ids_by_type,
    )

    schedule = output["schedule"]

    # - Get frontend

    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )
    m.push_row("stub", size=0)  # start with 1

    # calc start time
    start_t = int(custom_round(schedule.x[0], 12, "floor"))  # round to last hour
    start_time = cast_time(start_t)

    m.push(wrap_header(date=date, start_time=start_time, header="График работы цеха милкпроджект"))

    with m.push(start_time=start_time, axis=1):
        m.push(wrap_line(schedule))

    # - Update and return output

    output["frontend"] = m.root

    return output


def test():
    print(
        wrap_frontend(
            str(
                get_repo_path()
                / "app/data/static/samples/by_department/milk_project/План по варкам милкпроджект 3.xlsx"
            )
        )
    )


if __name__ == "__main__":
    test()
