from app.imports.runtime import *
from app.scheduler.frontend import draw_excel_frontend


def submit_schedule(
    name, schedule, frontend, path, prefix, style, open_file=False, split_file=False
):
    utils.makedirs(path)
    with code("Dump schedule as pickle file"):
        base_fn = f"Расписание {name}.pickle"
        if prefix:
            base_fn = prefix + " " + base_fn
        output_pickle_fn = os.path.join(path, base_fn)
        if split_file:
            output_pickle_fn = utils.SplitFile(output_pickle_fn).get_new()

        with open(output_pickle_fn, "wb") as f:
            pickle.dump(schedule.to_dict(), f)

    with code("Dump frontend as excel file"):
        base_fn = f"Расписание {name}.xlsx"
        if prefix:
            base_fn = prefix + " " + base_fn
        output_fn = os.path.join(path, base_fn)

        if split_file:
            output_fn = utils.SplitFile(output_fn).get_new()

        draw_excel_frontend(frontend, open_file=open_file, fn=output_fn, style=style)

    return {"schedule": schedule, "frontend": frontend}
