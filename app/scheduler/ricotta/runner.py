from app.imports.runtime import *
from app.scheduler.ricotta import *


def run_ricotta(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    output_directory="outputs/",
    output_prefix="",
):
    os.makedirs(output_directory)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)
    start_time = start_time or "07:00"

    if not schedule:
        schedule = make_schedule(boiling_plan_df, start_time=start_time)

    with code("Dump schedule as pickle file"):
        base_fn = "Расписание рикотта.pickle"
        if output_prefix:
            base_fn = output_prefix + " " + base_fn
        output_pickle_fn = os.path.join(output_directory, base_fn)
        output_pickle_fn = utils.SplitFile(output_pickle_fn).get_new()

        with open(output_pickle_fn, "wb") as f:
            pickle.dump(schedule.to_dict(), f)

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")

    with code("Dump frontend as excel file"):
        base_fn = "Расписание рикотта.xlsx"
        if output_prefix:
            base_fn = output_prefix + " " + base_fn
        output_fn = os.path.join(output_directory, base_fn)

        draw_excel_frontend(frontend, open_file=open_file, fn=output_fn, style=STYLE)

    return {"schedule": schedule, "frontend": frontend}
