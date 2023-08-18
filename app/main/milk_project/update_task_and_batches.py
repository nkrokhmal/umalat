from app.imports.runtime import *
from app.models import MilkProjectSKU
from app.scheduler.milk_project.boiling_plan import read_boiling_plan
from app.scheduler.milk_project.update_interval_times import update_interval_times
from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.cast_schedule import cast_schedule
from app.utils.milk_project.schedule_tasks import MilkProjectScheduleTask


def init_task(date, boiling_plan_df):
    return MilkProjectScheduleTask(df=boiling_plan_df, date=date, model=MilkProjectSKU, department="Милкпроджект")


def update_task_and_batches(schedule_obj):
    with code("Prepare"):
        wb = cast_schedule(schedule_obj)
        metadata = json.loads(utils.read_metadata(wb))
        date = utils.cast_datetime(metadata["date"])
        boiling_plan_df = read_boiling_plan(wb, first_batch_ids=metadata["first_batch_ids"])

    with code("Batch"):
        add_batch_from_boiling_plan_df(date, "Милкпроджект", boiling_plan_df)

    with code("Update"):
        schedule_task = init_task(date, boiling_plan_df)
        if len(boiling_plan_df) == 0:
            return schedule_task

        try:
            update_interval_times(wb, boiling_plan_df)
        except:
            logger.exception("Failed to update intervals", date=date, department_name="milk project")

            boiling_plan_df["start"] = ""
            boiling_plan_df["finish"] = ""

        schedule_task.update_schedule_task()
    return schedule_task
