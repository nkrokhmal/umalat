from utils_ak.openpyxl import cast_workbook

from app.imports.runtime import *


def cast_schedule(schedule_obj):
    if isinstance(schedule_obj, openpyxl.Workbook):
        return schedule_obj
    elif isinstance(schedule_obj, (list, tuple)):
        fn = os.path.join(flask.current_app.config["DYNAMIC_DIR"], *schedule_obj)
        return cast_workbook(fn)
    elif isinstance(schedule_obj, str):
        return cast_workbook(schedule_obj)
