from app.imports.runtime import *
from app.main import main


@main.route("/download_mozzarella_schedule", methods=["GET"])
@flask_login.login_required
def download_mozzarella_schedule():
    date = flask.request.args.get("date")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["SCHEDULE_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=f"{date} Расписание моцарелла.xlsx", as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_mozzarella_boiling_plan", methods=["GET"])
@flask_login.login_required
def download_mozzarella_boiling_plan():
    date = flask.request.args.get("date")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["BOILING_PLAN_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, filename=f"{date} План по варкам моцарелла.xlsx", as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response