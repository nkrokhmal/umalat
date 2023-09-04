from app.imports.runtime import *
from app.models import MozzarellaSKU
from app.scheduler.mozzarella.parse_schedule import parse_schedule
from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.mozzarella.schedule_task import MozzarellaScheduleTask
from app.utils.schedule import cast_schedule


def init_task(date, boiling_plan_df, df_packing):
    return MozzarellaScheduleTask(
        df=boiling_plan_df, date=date, model=MozzarellaSKU, department="Моцарелльный цех", df_packing=df_packing
    )


def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, "Расписание"))
    boiling_plan_df["interval_time"] = None

    interval_times = {}

    for boiling in schedule_info["boilings"]:
        interval_times[boiling["boiling_id"]] = boiling["interval_time"]

    boiling_plan_df["start"] = boiling_plan_df["absolute_batch_id"].apply(
        lambda batch_id: interval_times.get(batch_id, [None, None])[0]
    )
    boiling_plan_df["finish"] = boiling_plan_df["absolute_batch_id"].apply(
        lambda batch_id: interval_times.get(batch_id, [None, None])[1]
    )
    return boiling_plan_df


def update_task_and_batches(schedule_obj, boiling_plan_df=None):
    # - Prepare

    wb = cast_schedule(schedule_obj)
    metadata = json.loads(utils.read_metadata(wb))
    df_packing = read_additional_packing(wb)
    if boiling_plan_df is None:
        boiling_plan_df = read_boiling_plan(wb, first_batch_ids=metadata["first_batch_ids"])
    date = utils.cast_datetime(metadata["date"])

    # - Batch

    add_batch_from_boiling_plan_df(date, "Моцарельный цех", boiling_plan_df)

    # - Task

    try:
        update_interval_times(wb, boiling_plan_df)
    except:
        logger.exception("Failed to update intervals", date=date, department_name="mozzarella")

        boiling_plan_df["start"] = ""
        boiling_plan_df["finish"] = ""

    schedule_task = init_task(date, boiling_plan_df, df_packing)
    schedule_task.update_schedule_task()

    # - Return

    return schedule_task
