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


