from app.imports.runtime import *
from app.main import main


@main.route("/download_boiling_plan/<file_name>", methods=["POST", "GET"])
def download_boiling_plan(file_name):
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["BOILING_PLAN_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_sku_plan/<file_name>", methods=["POST", "GET"])
def download_sku_plan(file_name):
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["SKU_PLAN_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_stats/<file_name>", methods=["POST", "GET"])
def download_stats(file_name):
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["STATS_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, cache_timeout=0, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_schedule_plan/<file_name>", methods=["POST", "GET"])
def download_schedule_plan(file_name):
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["SCHEDULE_PLAN_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, cache_timeout=0, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_schedule_task/<file_name>", methods=["POST", "GET"])
def download_schedule_task(file_name):
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["TOTAL_SCHEDULE_TASK_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, cache_timeout=0, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_last_schedule_task", defaults={'check_date': False}, methods=["GET", "POST"])
def download_last_schedule_task(check_date):
    print(f"Check date id {check_date}")
    schedule_task_folder = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["TOTAL_SCHEDULE_TASK_FOLDER"],
    )
    schedules_task_filenames = os.listdir(schedule_task_folder)
    schedules_task_filenames = [filename for filename in schedules_task_filenames if filename.endswith(".csv")]
    last_filename = sorted(schedules_task_filenames, reverse=True)
    if len(last_filename) > 0:
        filename = last_filename[0]
        if check_date:
            date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            if filename.split('.')[0] != date:
                raise  Exception(f"There is no csv file for {date} date!")
            else:
                response = flask.send_from_directory(
                    directory=schedule_task_folder, filename=filename, cache_timeout=0, as_attachment=True
                )
                response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
                return response
        else:
            response = flask.send_from_directory(
                directory=schedule_task_folder, filename=filename, cache_timeout=0, as_attachment=True
            )
            response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
            return response
    else:
        raise Exception("There is no csv files in schedule task directory!")



