import os

import flask
import flask_login

from app.main import main


@main.route("/download_mascarpone_schedule", methods=["GET"])
@flask_login.login_required
def download_mascarpone_schedule():
    date = flask.request.args.get("date")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["SCHEDULE_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=f"{date} Расписание маскарпоне.xlsx", as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_mascarpone_boiling_plan", methods=["GET"])
@flask_login.login_required
def download_mascarpone_boiling_plan():
    date = flask.request.args.get("date")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["BOILING_PLAN_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=f"{date} План по варкам маскарпоне.xlsx", as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response
