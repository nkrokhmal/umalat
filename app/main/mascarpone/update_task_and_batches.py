import json

from loguru import logger
from utils_ak.code_block.code_block import code
from utils_ak.openpyxl.openpyxl_tools import read_metadata
from utils_ak.time.dt import cast_datetime

from app.models import MascarponeSKU
from app.scheduler.mascarpone.boiling_plan import read_boiling_plan
from app.scheduler.mascarpone.update_interval_times import update_interval_times
from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.mascarpone.schedule_task import MascarponeScheduleTask
from app.utils.schedule import cast_schedule


def init_task(date, boiling_plan_df):
    return MascarponeScheduleTask(df=boiling_plan_df, date=date, model=MascarponeSKU, department="Маскарпонный цех")


def update_task_and_batches(schedule_obj):
    with code("Prepare"):
        wb = cast_schedule(schedule_obj)
        metadata = json.loads(read_metadata(wb))
        boiling_plan_df = read_boiling_plan(wb, first_batch_ids=metadata["first_batch_ids"])
        date = cast_datetime(metadata["date"])

    with code("Batch"):
        add_batch_from_boiling_plan_df(date, "Маскарпоновый цех", boiling_plan_df)

    with code("Task"):
        try:
            update_interval_times(wb, boiling_plan_df)
        except:
            logger.exception("Failed to update intervals", date=date, department_name="mascarpone")

            boiling_plan_df["start"] = ""
            boiling_plan_df["finish"] = ""

        schedule_task = init_task(date, boiling_plan_df)
        schedule_task.update_schedule_task()
    return schedule_task


__all__ = [
    "update_task_and_batches",
    "init_task",
]
