from app.scheduler.contour_cleanings import *
from app.scheduler.submit import submit_schedule
from app.scheduler.load_schedules import *
from app.scheduler.load_properties.load_properties import *


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

            # todo maybe: need a check here?
            # assert_schedules_presence(
            #     schedules,
            #     raise_if_not_present=["ricotta"],
            #     warn_if_not_present=[
            #         "mozzarella",
            #         "butter",
            #         "adygea",
            #         "milk_project",
            #         "mascarpone",
            #     ],
            # )

            properties = load_properties(schedules, path=input_path, prefix=prefix)

        schedule = make_schedule(properties, **kwargs)
    frontend = wrap_frontend(schedule)
    return submit_schedule(
        "контурные мойки",
        schedule,
        frontend,
        prefix,
        STYLE,
        path=output_path,
        open_file=open_file,
    )
