from app.imports.runtime import *
from app.scheduler.contour_cleanings import *
from app.scheduler.frontend import *
from app.scheduler.submit import submit_schedule
from app.scheduler.load_schedules import *
from app.scheduler.load_properties import *


def run_contour_cleanings(
    input_path,
    output_path="outputs/",
    schedule=None,
    schedules=None,
    properties=None,
    prefix="",
    open_file=False,
    **kwargs,
):
    if not schedule:
        if not properties:
            if not schedules:
                schedules = load_schedules(input_path, prefix=prefix)
            assert_schedules_presence(
                schedules,
                raise_if_not_present=["mozzarella", "ricotta"],
                warn_if_not_present=["butter", "adygea", "milk_project", "mascarpone"],
            )

            properties = load_properties(schedules)

        schedule = make_schedule(properties, **kwargs)
    frontend = wrap_frontend(schedule)
    return submit_schedule(
        "контурные мойки",
        schedule,
        frontend,
        output_path,
        prefix,
        STYLE,
        open_file=open_file,
    )
