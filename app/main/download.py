import os.path

from app.imports.runtime import *
from app.main import main


DEPARTMENTS = ["mozzarella", "ricotta", "mascarpone", "butter", "milk_project", "adygea"]
DEPARTMENT_DICT = {
    "mozzarella": "Моцарелльный цех",
    "ricotta": "Рикоттный цех",
    "mascarpone": "Маскарпонный цех",
    "butter": "Маслоцех",
    "milk_project": "Милкпроджект",
    "adygea": "Адыгейский цех",
}


@main.route("/download_contour_washers", methods=["POST", "GET"])
@flask_login.login_required
def download_contour_washers():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["APPROVED_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_boiling_plan", methods=["POST", "GET"])
@flask_login.login_required
def download_boiling_plan():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["BOILING_PLAN_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_schedule_plan", methods=["POST", "GET"])
@flask_login.login_required
def download_schedule_plan():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["SCHEDULE_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, cache_timeout=0, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_schedule_task", methods=["POST", "GET"])
@flask_login.login_required
def download_schedule_task():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["TASK_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, cache_timeout=0, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_last_schedule_task", defaults={'check_date': False}, methods=["GET", "POST"])
def download_last_schedule_task(check_date):
    dates = [folder for folder in os.listdir(flask.current_app.config["DYNAMIC_DIR"]) if folder.startswith('20')]
    task_dirs = [os.path.join(
            os.path.dirname(flask.current_app.root_path),
            flask.current_app.config["DYNAMIC_DIR"],
            x,
            flask.current_app.config["TASK_FOLDER"],
            f"{x}.csv"
        )
        for x in dates]
    task_dirs = [x for x in task_dirs if os.path.exists(x)]
    task_dirs = sorted(task_dirs, reverse=True)
    if len(task_dirs) > 0:
        last_dir, filename = os.path.split(task_dirs[0])
        response = flask.send_from_directory(
            directory=last_dir, filename=filename, cache_timeout=0, as_attachment=True
        )
        response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
        return response
    else:
        raise Exception("There is no csv files in schedule task directory!")


@main.route("/download_last_boiling_schedule_task/<department>")
def download_last_boiling_schedule_task(department):
    if department not in DEPARTMENTS:
        raise Exception("Wrong department name")

    dates = [folder for folder in os.listdir(flask.current_app.config["DYNAMIC_DIR"]) if folder.startswith('20')]
    task_dirs = [os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        x,
        flask.current_app.config["TASK_FOLDER"],
        f"{x} {DEPARTMENT_DICT[department]}.csv"
    )
        for x in dates]
    task_dirs = [x for x in task_dirs if os.path.exists(x)]
    task_dirs = sorted(task_dirs, reverse=True)
    if len(task_dirs) > 0:
        last_dir, filename = os.path.split(task_dirs[0])
        response = flask.send_from_directory(
            directory=last_dir, filename=filename, cache_timeout=0, as_attachment=True
        )
        response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
        return response
    else:
        raise Exception("There is no csv files in schedule task directory!")







