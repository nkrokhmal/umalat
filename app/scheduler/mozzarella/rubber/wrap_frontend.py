import xml.sax

from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from utils_ak.block_tree import BlockMaker, add_push
from utils_ak.os import open_file_in_os

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.brynza.draw_frontend2.style import STYLE
from app.scheduler.brynza.draw_frontend2.wrap_frontend2 import wrap_frontend2
from app.scheduler.brynza.draw_frontend.wrap_frontend import wrap_frontend
from app.scheduler.frontend_utils import draw_excel_frontend
from app.scheduler.mozzarella.rubber.make_schedule import make_schedule


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
