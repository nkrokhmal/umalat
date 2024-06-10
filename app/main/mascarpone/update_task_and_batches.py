import json

from loguru import logger
from utils_ak.code_block.code_block import code
from utils_ak.openpyxl.openpyxl_tools import read_metadata
from utils_ak.time.dt import cast_datetime

from app.enum import DepartmentName
from app.main.mascarpone.update_interval_times import update_interval_times
from app.models import MascarponeSKU
from app.scheduler.mascarpone.to_boiling_plan import to_boiling_plan
from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.mascarpone.schedule_task import MascarponeScheduleTask
from app.utils.schedule import cast_schedule


def init_task(date, boiling_plan_df):
    return MascarponeScheduleTask(df=boiling_plan_df, date=date, model=MascarponeSKU, department="Маскарпонный цех")


def update_task_and_batches(schedule_obj):

    # - Prepare

    wb = cast_schedule(schedule_obj)
    metadata = json.loads(read_metadata(wb))
    boiling_plan_df = to_boiling_plan(wb, first_batch_ids_by_type=metadata["first_batch_ids"], unwind=True)
    date = cast_datetime(metadata["date"])

    # - Batch

    add_batch_from_boiling_plan_df(date, DepartmentName.MASCARPONE, boiling_plan_df)

    # - Task

    try:
        update_interval_times(wb, boiling_plan_df)
    except:
        logger.exception("Failed to update intervals", date=date, department_name="mascarpone")

        boiling_plan_df["start"] = ""
        boiling_plan_df["finish"] = ""

    schedule_task = init_task(date, boiling_plan_df)
    schedule_task.update_schedule_task()

    # - Return

    return schedule_task


__all__ = [
    "update_task_and_batches",
    "init_task",
]
