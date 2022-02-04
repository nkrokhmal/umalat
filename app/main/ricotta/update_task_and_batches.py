from app.imports.runtime import *

from app.utils.batches import add_batch_from_boiling_plan_df
from app.utils.schedule import cast_schedule

from app.models import RicottaSKU
from app.scheduler.ricotta.boiling_plan import read_boiling_plan
from app.scheduler.ricotta.update_interval_times import update_interval_times
from app.utils.ricotta.schedule_tasks import RicottaScheduleTask


def init_task(date, boiling_plan_df):
    return RicottaScheduleTask(
        df=boiling_plan_df, date=date, model=RicottaSKU, department="Рикоттный цех"
    )


def update_task_and_batches(schedule_obj):
    with code('Prepare'):
        wb = cast_schedule(schedule_obj)
        metadata = json.loads(utils.read_metadata(wb))
        boiling_plan_df = read_boiling_plan(wb, first_batch_ids=metadata['first_batch_ids'])
        date = utils.cast_datetime(metadata['date'])

    with code('Batch'):
        add_batch_from_boiling_plan_df(date, 'Рикоттный цех', boiling_plan_df)

    with code('Task'):
        try:
            update_interval_times(wb, boiling_plan_df)
        except:
            # todo later: warning
            boiling_plan_df['start'] = ''
            boiling_plan_df['finish'] = ''

        schedule_task = init_task(date, boiling_plan_df)
        schedule_task.update_schedule_task()
    return schedule_task