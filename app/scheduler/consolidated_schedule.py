from app.imports.runtime import *
from app.scheduler import draw_excel_frontend, init_schedule_workbook
from utils_ak.block_tree import *


def draw_consolidated(schedules):
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

    draw_excel_frontend(frontend, STYLE, wb=wb, open_file=True)


def test():
    fns = {
        "mozzarella": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание моцарелла.pickle",
        "mascarpone": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание маскарпоне.pickle",
        "butter": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание масло.pickle",
        "milk_project": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание милкпроджект.pickle",
        "ricotta": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Расписание рикотта.pickle",
        "contour_cleanings": "/Users/arsenijkadaner/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/schedule_dict/2021-01-01 Контурные мойки.pickle",
    }
    schedules = {}
    for key, fn in fns.items():
        with open(fn, "rb") as f:
            schedules[key] = ParallelepipedBlock.from_dict(pickle.load(f))

    # print(schedules["ricotta"])
    draw_consolidated(schedules)


if __name__ == "__main__":
    test()
