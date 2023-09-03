import os
import pickle

from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.os.os_tools import makedirs
from utils_ak.split_file.split_file import SplitFile

from app.scheduler.frontend import draw_excel_frontend


def submit_schedule(
    name: str,
    schedule,
    frontend,
    style: dict,
    prefix: str = "",
    template_wb=None,
    path: str = None,
    open_file: bool = False,
    split_file: bool = False,
):
    # - Preprocess arguments

    if prefix:
        prefix = prefix + " "

    # - Make directories

    makedirs(path)

    # - Dump schedule as pickle file

    if path:
        base_fn = f"{prefix}Расписание {name}.pickle"
        output_pickle_fn = os.path.join(path, base_fn)

        if split_file:
            output_pickle_fn = SplitFile(output_pickle_fn).get_new()

        with open(output_pickle_fn, "wb") as f:
            pickle.dump(schedule.to_dict(), f)

    # - Get output fn

    output_fn = None

    if path:
        base_fn = f"{prefix}Расписание {name}.xlsx"

        output_fn = os.path.join(path, base_fn)

        if split_file:
            output_fn = SplitFile(output_fn).get_new()

    # - Draw excel frontend

    workbook = draw_excel_frontend(frontend, open_file=open_file, fn=output_fn, style=style, wb=template_wb)

    # - Return

    return {"schedule": schedule, "frontend": frontend, "workbook": workbook}
