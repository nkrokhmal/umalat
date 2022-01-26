from app.imports.runtime import *

from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.schedule import cast_schedule

from app.models import MilkProjectSKU
from app.scheduler.milk_project.boiling_plan import read_boiling_plan
from app.scheduler.milk_project.update_interval_times import update_interval_times
from app.utils.milk_project.schedule_tasks import MilkProjectScheduleTask


def init_task(date, boiling_plan_df):
    return MilkProjectScheduleTask(
        df=boiling_plan_df, date=date, model=MilkProjectSKU, department="Милкпроджект"
    )


def update_task_and_batches(schedule_obj):
    with code('Prepare'):
        wb = cast_schedule(schedule_obj)
        metadata = json.loads(utils.read_metadata(wb))
        boiling_plan_df = read_boiling_plan(wb, first_batch_ids=metadata['first_batch_ids'])
        boiling_plan_df = update_interval_times(wb, boiling_plan_df)
        date = utils.cast_datetime(metadata['date'])
    logger.debug('Updating milk_project task', date=date)
    with code('Update'):
        add_batch_from_boiling_plan_df(date, 'Милкпроджект', boiling_plan_df)
        schedule_task = init_task(date, boiling_plan_df)
        schedule_task.update_schedule_task()
    return schedule_task