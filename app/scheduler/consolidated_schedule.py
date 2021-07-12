from app.imports.runtime import *
from app.scheduler import draw_excel_frontend, init_schedule_workbook
from utils_ak.block_tree import *


def run_consolidated(path, prefix="", open_file=False):
    schedules = {}
    for a, b in [
        ["mozzarella", "Расписание моцарелла"],
        ["mascarpone", "Расписание маскарпоне"],
        ["butter", "Расписание масло"],
        ["milk_project", "Расписание милкпроджект"],
        ["ricotta", "Расписание рикотта"],
        ["contour_cleanings", "Расписание контурные мойки"],
    ]:
        fn = os.path.join(path, prefix + " " + b + ".pickle")
        with open(fn, "rb") as f:
            schedules[a] = ParallelepipedBlock.from_dict(pickle.load(f))

    wb = init_schedule_workbook()

    cur_depth = 0

    from app.scheduler.mozzarella import wrap_frontend, STYLE

    frontend = wrap_frontend(schedules["mozzarella"])
    depth = frontend.y[1]
    frontend.props.update(x=(frontend.x[0], frontend.x[1] + cur_depth))
    cur_depth += depth
    draw_excel_frontend(frontend, STYLE, wb=wb)

    from app.scheduler.ricotta import wrap_frontend, STYLE

    frontend = wrap_frontend(schedules["ricotta"])
    depth = frontend.y[1]
    frontend.props.update(x=(frontend.x[0], frontend.x[1] + cur_depth))
    cur_depth += depth

    draw_excel_frontend(frontend, STYLE, wb=wb)

    from app.scheduler.mascarpone import wrap_frontend, STYLE

    frontend = wrap_frontend(schedules["mascarpone"])
    depth = frontend.y[1]
    frontend.props.update(x=(frontend.x[0], frontend.x[1] + cur_depth))
    cur_depth += depth

    draw_excel_frontend(frontend, STYLE, wb=wb)

    from app.scheduler.butter import wrap_frontend, STYLE

    frontend = wrap_frontend(schedules["butter"])
    depth = frontend.y[1]
    frontend.props.update(x=(frontend.x[0], frontend.x[1] + cur_depth))
    cur_depth += depth

    draw_excel_frontend(frontend, STYLE, wb=wb)

    from app.scheduler.milk_project import wrap_frontend, STYLE

    frontend = wrap_frontend(schedules["milk_project"])
    depth = frontend.y[1]
    frontend.props.update(x=(frontend.x[0], frontend.x[1] + cur_depth))
    cur_depth += depth

    draw_excel_frontend(frontend, STYLE, wb=wb)

    from app.scheduler.contour_cleanings import wrap_frontend, STYLE

    frontend = wrap_frontend(schedules["contour_cleanings"])
    depth = frontend.y[1]
    frontend.props.update(x=(frontend.x[0], frontend.x[1] + cur_depth))
    cur_depth += depth

    # todo maybe: copy-paste from submit_schedule
    with code("Dump frontend as excel file"):
        base_fn = f"Расписание общее.xlsx"
        if prefix:
            base_fn = prefix + " " + base_fn
        output_fn = os.path.join(path, base_fn)

        draw_excel_frontend(
            frontend, open_file=open_file, wb=wb, fn=output_fn, style=STYLE
        )


def test():
    run_consolidated(
        "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/",
        prefix="2021-01-01",
        open_file=True,
    )


if __name__ == "__main__":
    test()
