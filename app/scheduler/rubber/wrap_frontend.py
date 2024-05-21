from datetime import datetime
from typing import Optional

from utils_ak.block_tree import BlockMaker, add_push

from app.scheduler.brynza.draw_frontend.wrap_frontend import wrap_frontend
from app.scheduler.rubber.make_schedule import make_schedule


def wrap_frontend(
    boiling_plan: str,
    date: Optional[datetime] = None,
    start_time: str = "07:00",
) -> dict:
    # - Get schedule

    output = make_schedule(boiling_plan=boiling_plan, start_time=start_time)
    schedule = output["schedule"]

    # - Plot boilings

    date = date or datetime.now()

    # - Init block maker

    m = BlockMaker(
        "frontend",
        default_row_width=3,
        default_col_width=1,
        # props
        axis=1,
    )

    if len(schedule["packing_group", True]) == 0:
        output["frontend"] = m.root
        return output

    # - Make packing groups

    for packing_group in schedule["packing_group"]:
        m.block(
            "packing_group",
            size=(packing_group.size[0], 1),
            x=(packing_group.x[0], 0),
            push_func=add_push,
            kg=packing_group.props["kg"],
            sku=packing_group.props["sku"],
        )

    for key in ["packing", "long_switch", "short_switch"]:
        for block in schedule.iter(cls=key):
            m.block(m.copy(block, with_props=True), size=(block.size[0], 2), x=(block.x[0], 1), push_func=add_push)

    for key in ["preparation", "refurbishment", "cleaning"]:
        for block in schedule.iter(cls=key):
            m.block(m.copy(block, with_props=True), size=(block.size[0], 3), x=(block.x[0], 0), push_func=add_push)

    # - Add rubber_ prefix to all blocks

    for block in m.root.iter():
        block.props.update(cls=f"rubber_{block.props['cls']}")

    # - Return

    output["frontend"] = m.root

    return output


def test():
    print(
        wrap_frontend(
            boiling_plan="""/Users/marklidenberg/Desktop/2024.04.19 терка мультиголовы/2024-03-08 План по варкам моцарелла.xlsx"""
        )["frontend"]
    )


if __name__ == "__main__":
    test()
