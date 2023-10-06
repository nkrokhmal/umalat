from loguru import logger
from utils_ak.openpyxl import read_metadata
from utils_ak.time import cast_datetime

from app.imports.runtime import *
from app.models import AdygeaSKU
from app.scheduler.adygea.to_boiling_plan.to_boiling_plan import to_boiling_plan
from app.scheduler.milk_project.parse_schedule import parse_schedule

# from app.scheduler.milk_project.to_boiling_plan import to_boiling_plan
from app.utils.adygea.schedule_tasks import AdygeaScheduleTask
from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.schedule import cast_schedule


def init_task(date, boiling_plan_df):
    return AdygeaScheduleTask(df=boiling_plan_df, date=date, model=AdygeaSKU, department="Адыгейский цех")


def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, "Расписание"))

    interval_times = {}

    for boiling in schedule_info.get("adygea_boilings", []):
        interval_times[boiling["boiling_id"]] = boiling["interval_time"]

    boiling_plan_df["start"] = boiling_plan_df["batch_id"].apply(
        lambda batch_id: interval_times.get(batch_id, ["", ""])[0]
    )
    boiling_plan_df["finish"] = boiling_plan_df["batch_id"].apply(
        lambda batch_id: interval_times.get(batch_id, ["", ""])[1]
    )
    return boiling_plan_df


def update_task_and_batches(schedule_obj):
    # - Prepare

    wb = cast_schedule(schedule_obj)
    metadata = json.loads(read_metadata(wb))
    date = cast_datetime(metadata["date"])
    boiling_plan_df = to_boiling_plan(wb, first_batch_ids_by_type=metadata["first_batch_ids"])

    # - Batch

    add_batch_from_boiling_plan_df(date, "Адыгейский цех", boiling_plan_df)

    # - Task

    schedule_task = init_task(date, boiling_plan_df)
    if len(boiling_plan_df) == 0:
        return schedule_task

    try:
        update_interval_times(wb, boiling_plan_df)
    except:
        logger.exception("Failed to update intervals", date=date, department_name="adygea")

        boiling_plan_df["start"] = ""
        boiling_plan_df["finish"] = ""

    schedule_task.update_schedule_task()

    # - Return

    return schedule_task
