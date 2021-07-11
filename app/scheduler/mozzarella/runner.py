from app.imports.runtime import *
from app.scheduler.mozzarella import *


def run_mozzarella(
    fn=None,
    schedule=None,
    open_file=False,
    start_times=None,
    first_boiling_id=1,
    optimize=True,
    output_directory="schedules/",
    output_prefix="",
):
    start_times = start_times or {LineName.WATER: "02:00", LineName.SALT: "06:00"}

    if not schedule:
        schedule = make_schedule(
            fn,
            optimize=optimize,
            start_times=start_times,
            first_boiling_id=first_boiling_id,
        )

    with code("Dump schedule as pickle file"):
        base_fn = "Расписание моцарелла.pickle"
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
        base_fn = "Расписание моцарелла.xlsx"
        if output_prefix:
            base_fn = output_prefix + " " + base_fn
        output_fn = os.path.join(output_directory, base_fn)

        draw_excel_frontend(frontend, open_file=open_file, fn=output_fn, style=STYLE)

    return {"schedule": schedule, "frontend": frontend}
