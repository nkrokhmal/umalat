from app.imports.runtime import *
from app.scheduler import (
    run_contour_cleanings,
    run_consolidated,
    run_ricotta,
    run_butter,
    run_mascarpone,
    run_mozzarella,
    run_milk_project,
    run_adygea,
)


def _test_day(
    input_path,
    prefix,
    output_path="outputs/",
    input_params=None,
    open_file=False,
    run_boiling_plans=True,
):
    input_params = input_params or {}

    if run_boiling_plans:
        run_mozzarella(
            os.path.join(input_path, prefix + " " + "План по варкам моцарелла.xlsx"),
            prefix=prefix,
            path=output_path,
            **input_params.get("mozzarella", {})
        )
        run_ricotta(
            os.path.join(input_path, prefix + " " + "План по варкам рикотта.xlsx"),
            prefix=prefix,
            path=output_path,
            **input_params.get("ricotta", {})
        )
        run_mascarpone(
            os.path.join(input_path, prefix + " " + "План по варкам маскарпоне.xlsx"),
            prefix=prefix,
            path=output_path,
            **input_params.get("mascarpone", {})
        )
        run_butter(
            os.path.join(input_path, prefix + " " + "План по варкам масло.xlsx"),
            prefix=prefix,
            path=output_path,
            **input_params.get("butter", {})
        )
        run_milk_project(
            os.path.join(input_path, prefix + " " + "План по варкам милкпроджект.xlsx"),
            prefix=prefix,
            path=output_path,
            **input_params.get("milk_project", {})
        )
        run_adygea(
            os.path.join(input_path, prefix + " " + "План по варкам адыгейский.xlsx"),
            prefix=prefix,
            path=output_path,
            **input_params.get("milk_project", {})
        )
    elif input_path != output_path:
        for fn in utils.list_files(input_path):
            utils.copy_path(fn, os.path.join(output_path, os.path.basename(fn)))
    run_contour_cleanings(
        output_path,
        output_path=output_path,
        prefix=prefix,
        **input_params.get("contour_cleanings", {})
    )
    run_consolidated(
        output_path,
        output_path=output_path,
        prefix=prefix,
        open_file=open_file,
    )


# todo: make proper test
def _test_batch(same_output_path=False):
    paths = glob.glob(config.abs_path("app/data/static/samples/inputs/by_day/*"))

    for path in tqdm.tqdm(paths):
        prefix = os.path.basename(path)
        output_path = "outputs/" if not same_output_path else path
        _test_day(
            input_path=path,
            output_path=output_path,
            prefix=prefix,
            open_file=False,
        )


# if __name__ == "__main__":
#     _test_day(
#         input_path="/Users/marklidenberg/Yandex.Disk.localized/umalat/2021-09-07/approved",
#         prefix="2021-09-07",
#         open_file=True,
#         # input_params={
#         #     "contour_cleanings": {
#         #         "butter_end_time": "19:00:00",
#         #         "milk_project_end_time": "11:00:00",
#         #         "adygea_end_time": "14:00:00",
#         #         "shipping_line": False,
#         #         "is_bar12_present": False,
#         #     }
#         # },
#         run_boiling_plans=False,
#     )
# _test_batch(True)
