from app.imports.runtime import *

from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.schedule import cast_schedule

from app.models import ButterSKU
from app.scheduler.butter.boiling_plan import read_boiling_plan
from app.scheduler.butter.update_interval_times import update_interval_times
from app.utils.butter.schedule_tasks import ButterScheduleTask


def init_task(date, boiling_plan_df):
    return ButterScheduleTask(
        df=boiling_plan_df, date=date, model=ButterSKU, department='Маслоцех'
    )


def update_task_and_batches(schedule_obj):
    with code('Prepare'):
        wb = cast_schedule(schedule_obj)
        metadata = json.loads(utils.read_metadata(wb))
        boiling_plan_df = read_boiling_plan(wb, first_batch_ids=metadata['first_batch_ids'])
        boiling_plan_df = update_interval_times(wb, boiling_plan_df)
        date = utils.cast_datetime(metadata['date'])
    logger.debug('Updating butter task', date=date)
    with code('Update'):
        add_batch_from_boiling_plan_df(date, 'Масло цех', boiling_plan_df)
        schedule_task = init_task(date, boiling_plan_df)
        schedule_task.update_schedule_task()
    return schedule_task