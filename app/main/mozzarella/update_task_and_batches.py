from app.imports.runtime import *
from app.models import MozzarellaSKU
from app.scheduler.mozzarella.boiling_plan import read_additional_packing, read_boiling_plan
from app.scheduler.mozzarella.update_interval_times import update_interval_times
from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.cast_schedule import cast_schedule
from app.utils.mozzarella.schedule_task import MozzarellaScheduleTask


def init_task(date, boiling_plan_df, df_packing):
    return MozzarellaScheduleTask(
        df=boiling_plan_df, date=date, model=MozzarellaSKU, department="Моцарелльный цех", df_packing=df_packing
    )


def update_task_and_batches(schedule_obj, boiling_plan_df=None):
    with code("Prepare"):
        wb = cast_schedule(schedule_obj)
        metadata = json.loads(utils.read_metadata(wb))
        df_packing = read_additional_packing(wb)
        if boiling_plan_df is None:
            boiling_plan_df = read_boiling_plan(wb, first_batch_ids=metadata["first_batch_ids"])
        date = utils.cast_datetime(metadata["date"])

    with code("Batch"):
        add_batch_from_boiling_plan_df(date, "Моцарельный цех", boiling_plan_df)

    with code("Task"):
        try:
            update_interval_times(wb, boiling_plan_df)
        except:
            logger.exception("Failed to update intervals", date=date, department_name="mozzarella")

            boiling_plan_df["start"] = ""
            boiling_plan_df["finish"] = ""

        schedule_task = init_task(date, boiling_plan_df, df_packing)
        schedule_task.update_schedule_task()
    return schedule_task
