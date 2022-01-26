from app.imports.runtime import *

from app.models import ButterSKU
from app.scheduler.butter.boiling_plan import read_boiling_plan
from app.scheduler.butter.parser_new import parse_schedule
from app.scheduler.butter.update_interval_times import update_interval_times
from app.utils.butter.schedule_tasks import ButterScheduleTask
from app.utils.files.utils import save_schedule, cast_dynamic_fn
from app.utils.batches import *


def init_task(date, boiling_plan_df):
    return ButterScheduleTask(
        df=boiling_plan_df, date=date, model=ButterSKU, department='Маслоцех'
    )


def update_task_from_approved_schedule(date, basename):
    logger.debug('Updating butter task', date=date, basename=basename)
    full_fn = cast_dynamic_fn(date.strftime('%Y-%m-%d'),
                              flask.current_app.config["SCHEDULE_FOLDER"],
                              basename)
    with code('Prepare'):
        wb = utils.cast_workbook(full_fn)
        metadata = json.loads(utils.read_metadata(wb))
        boiling_plan_df = read_boiling_plan(wb, first_batch_ids=metadata['first_batch_ids'])
        boiling_plan_df = update_interval_times(wb, boiling_plan_df)
    with code('Update'):
        add_batch_from_boiling_plan_df(date, 'Масло цех', boiling_plan_df)
        schedule_task = init_task(date, boiling_plan_df)
        schedule_task.update_schedule_task()

    return schedule_task