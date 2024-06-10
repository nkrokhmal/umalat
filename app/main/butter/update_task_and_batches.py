from loguru import logger
from utils_ak.openpyxl import read_metadata
from utils_ak.time import cast_datetime

from app.imports.runtime import *
from app.models import ButterSKU
from app.scheduler.butter.parse_schedule import parse_schedule
from app.scheduler.butter.to_boiling_plan import to_boiling_plan
from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.butter.schedule_tasks import ButterScheduleTask
from app.utils.schedule import cast_schedule


def init_task(date, boiling_plan_df):
    return ButterScheduleTask(df=boiling_plan_df, date=date, model=ButterSKU, department="Маслоцех")


def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, "Расписание"))

    if len(boiling_plan_df) == 0:
        return boiling_plan_df

    boilings = schedule_info.get("boilings", [])
    boilings = list(sorted(boilings, key=lambda b: b["interval"][0]))

    boiling_plan_df["start"] = ""
    boiling_plan_df["finish"] = ""

    for i, (batch_id, grp) in enumerate(boiling_plan_df.groupby("absolute_batch_id")):
        boiling_plan_df.loc[grp.index, "start"] = boilings[i]["interval_time"][0]
        boiling_plan_df.loc[grp.index, "finish"] = boilings[i]["interval_time"][1]
    return boiling_plan_df


def update_task_and_batches(schedule_obj):

    # - Prepare

    wb = cast_schedule(schedule_obj)
    metadata = json.loads(read_metadata(wb))
    boiling_plan_df = to_boiling_plan(wb, first_batch_ids_by_type=metadata["first_batch_ids"])
    date = cast_datetime(metadata["date"])

    # - Batch

    add_batch_from_boiling_plan_df(date, "Масло цех", boiling_plan_df)

    # - Task

    try:
        update_interval_times(wb, boiling_plan_df)
    except:
        logger.exception("Failed to update intervals", date=date, department_name="butter")

        boiling_plan_df["start"] = ""
        boiling_plan_df["finish"] = ""

    schedule_task = init_task(date, boiling_plan_df)
    schedule_task.update_schedule_task()

    # - Return

    return schedule_task
