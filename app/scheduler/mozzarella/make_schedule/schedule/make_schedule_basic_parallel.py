# - Set os so that db is created properly in parallel mode
import os


os.environ["APP_ENVIRONMENT"] = "parallel"

# - Define function that will be called in parallel


def make_schedule_basic_parallel(**kwargs):
    from app.scheduler.mozzarella.make_schedule.schedule.make_schedule_basic import make_schedule_basic

    return make_schedule_basic(**kwargs)
