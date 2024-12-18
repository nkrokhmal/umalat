import time

from datetime import datetime
from pathlib import Path
from typing import Optional

import openpyxl

from openpyxl import Workbook
from utils_ak.os import open_file_in_os

from app.enum import LineName
from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.frontend_utils import draw_excel_frontend
from app.scheduler.mozzarella.draw_frontend.style import STYLE
from app.scheduler.mozzarella.wrap_frontend import wrap_frontend
from app.utils.mozzarella.boiling_plan_draw import draw_boiling_plan_merged
from app.utils.mozzarella.parse_schedule_json import prepare_schedule_json


def draw_frontend(
    boiling_plan: str,
    date: Optional[datetime] = None,
    workbook: Workbook = None,
    saturate=True,
    normalization=True,
    validate=True,
    first_batch_ids_by_type={"mozzarella": 1},
    # - Make schedule basic_example kwargs
    exact_start_time_line_name=None,
    optimize_cleanings=False,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    rubber_start_time="07:00",
    start_configuration=None,
) -> dict:
    # - Wrap frontend

    output = wrap_frontend(
        boiling_plan=boiling_plan,
        first_batch_ids_by_type=first_batch_ids_by_type,
        saturate=saturate,
        normalization=normalization,
        validate=validate,
        rubber_start_time=rubber_start_time,
        # - Make schedule basic_example kwargs
        date=date,
        optimize_cleanings=optimize_cleanings,
        start_times=start_times,
        start_configuration=start_configuration,
        exact_start_time_line_name=exact_start_time_line_name,
    )

    # - Draw frontend

    output["workbook"] = draw_excel_frontend(
        frontend=output["frontend"],
        style=STYLE,
        open_file=False,
        fn=None,
        wb=workbook,
    )

    # - Return

    return output


def test():
    from utils_ak.loguru import configure_loguru

    configure_loguru(level="TRACE")

    # - Ignore warnings

    import warnings

    warnings.filterwarnings("ignore")

    # - Draw frontend

    started_at = time.time()

    repo_path = __file__.split("app")[0][:-1]

    # fn = str(
    #     Path(repo_path) / "app/data/static/samples/by_department/mozzarella/2024-01-10 План по варкам моцарелла.xlsx"
    # )

    schedule_wb = openpyxl.load_workbook(
        filename=Path(repo_path) / "app/data/static/templates/constructor_schedule.xlsx"
    )
    output = draw_frontend(
        boiling_plan=str(
            get_repo_path() / "app/data/static/samples/by_department/mozzarella/sample_schedule_mozzarella.xlsx"
            # get_repo_path() / "app/data/static/samples/by_department/rubber/sample_rubber_schedule.xlsx"
        ),
        workbook=schedule_wb,
        start_times={LineName.SALT: "09:00", LineName.WATER: "12:00"},
        exact_start_time_line_name=LineName.SALT,
        first_batch_ids_by_type={"mozzarella": 415},
        # start_configuration=[
        #     LineName.WATER if value == "В" else LineName.SALT
        #     for value in "В-С-В-С-В-С-В-С-В-С-В-С-В-С-В-С-С-В-С-В-С-В-С-В-С-С-С-С-С-С-С".split("-")  # 4
        # ],
    )

    schedule_json = output["schedule"].to_dict(
        props=[
            {"key": "x", "value": lambda b: list(b.props["x"])},
            {"key": "size", "value": lambda b: list(b.props["size"])},
            {"key": "cleaning_type", "cls": "cleaning"},
            {
                "key": "boiling_group_df",
                "cls": "boiling",
            },
        ]
    )
    cleanings = [x for x in schedule_json["children"][0]["children"] if x["cls"] == "cleaning"]
    schedule_df = prepare_schedule_json(schedule_json, cleanings)
    schedule_wb = draw_boiling_plan_merged(schedule_df, output["workbook"])

    schedule_wb.save("/tmp/schedule_mozzarella.xlsx")
    open_file_in_os("/tmp/schedule_mozzarella.xlsx")

    print("Elapsed", time.time() - started_at)


if __name__ == "__main__":
    test()
    # print(cast_t('01:00:35') - cast_t('01:40'))
