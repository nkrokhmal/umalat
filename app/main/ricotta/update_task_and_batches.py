from loguru import logger
from utils_ak.openpyxl import read_metadata
from utils_ak.time import cast_datetime

from app.imports.runtime import *
from app.main.ricotta.update_interval_times import update_interval_times
from app.models import RicottaSKU
from app.scheduler.ricotta.to_boiling_plan import to_boiling_plan
from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.ricotta.schedule_tasks import RicottaScheduleTask
from app.utils.schedule import cast_schedule


def init_task(date, boiling_plan_df):
    return RicottaScheduleTask(df=boiling_plan_df, date=date, model=RicottaSKU, department="Рикоттный цех")


def update_task_and_batches(schedule_obj):
    # - Prepare

    wb = cast_schedule(schedule_obj)
    metadata = json.loads(read_metadata(wb))
    boiling_plan_df = to_boiling_plan(wb, first_batch_ids_by_type=metadata["first_batch_ids"])
    date = cast_datetime(metadata["date"])

    # - Batch

    add_batch_from_boiling_plan_df(date, "Рикоттный цех", boiling_plan_df)

    # - Task

    try:
        update_interval_times(wb, boiling_plan_df)
    except:
        logger.exception("Failed to update intervals", date=date, department_name="ricotta")

        boiling_plan_df["start"] = ""
        boiling_plan_df["finish"] = ""

    schedule_task = init_task(date, boiling_plan_df)
    schedule_task.update_schedule_task()

    # - Return

    return schedule_task
