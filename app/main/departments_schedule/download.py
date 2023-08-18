from app.imports.runtime import *
from app.main import main


@main.route("/download_departments_schedule", methods=["GET"])
@flask_login.login_required
def download_departments_schedule():
    date = flask.request.args.get("date")
    uploads = config.abs_path("app/data/dynamic/{}/approved/".format(date))
    response = flask.send_from_directory(
        directory=uploads, filename=f"{date} Расписание общее.xlsx", as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response
