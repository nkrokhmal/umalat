from collections import OrderedDict
import flask_paginate
from app.utils.files.update import update_data_structure
from app.imports.runtime import *
from app.main import main


def get_department(filename):
    filename_without_ext = filename.split('.')[0]
    return "моцарелла" if len(filename_without_ext.split(' ')) < 3 else filename_without_ext.split(' ')[-1]


def get_metadata(data, offset=0, per_page=10):
    keys = list(data.keys())[offset: offset + per_page]
    result = OrderedDict((key, data[key]) for key in keys if key in data)
    return OrderedDict(sorted(result.items(), reverse=True))


def is_approved(filename, date):
    return os.path.exists(
        os.path.join(
            flask.current_app.config['DYNAMIC_DIR'],
            date,
            "approved",
            filename,
        )
    )


@main.route("/update_data", methods=["GET"])
def update_data():
    update_data_structure("boiling_plan")
    update_data_structure("schedule_plan")
    update_data_structure("schedule_task")
    response = flask.jsonify({"message": "Ok"})
    response.status_code = 200
    return response


@main.route("/download_schedules/<int:page>", methods=["GET"])
@flask_login.login_required
def download_schedules(page):
    date_dirs = next(os.walk(flask.current_app.config["DYNAMIC_DIR"]))[1]
    schedules_metadata = {}

    def is_date(string):
        try:
            _ = datetime.strptime(string, flask.current_app.config["DATE_FORMAT"])
            return True
        except:
            return False

    for date_dir in date_dirs:
        if is_date(date_dir):
            schedules_metadata[date_dir] = {}
            schedule_dir = os.path.join(flask.current_app.config["DYNAMIC_DIR"], date_dir, "schedule")
            if os.path.exists(schedule_dir):
                schedules_filenames = os.listdir(schedule_dir)
                for schedules_filename in schedules_filenames:
                    department = get_department(schedules_filename)
                    if department not in schedules_metadata[date_dir].keys():
                        schedules_metadata[date_dir][department] = {}
                        schedules_metadata[date_dir][department]['filename'] = schedules_filename
                        schedules_metadata[date_dir][department]['is_approved'] = is_approved(schedules_filename, date_dir)
            task_dir = os.path.join(flask.current_app.config["DYNAMIC_DIR"], date_dir, "task")
            if os.path.exists(task_dir):
                task_filename = os.listdir(task_dir)[0]
                if "task" not in schedules_metadata[date_dir].keys():
                    schedules_metadata[date_dir]["task"] = {}
                    schedules_metadata[date_dir]["task"]['filename'] = task_filename
    schedules_metadata = OrderedDict(sorted(schedules_metadata.items(), reverse=True))

    schedules_result = get_metadata(
        schedules_metadata,
        offset=(page - 1) * flask.current_app.config["SKU_PER_PAGE"],
        per_page=flask.current_app.config["SKU_PER_PAGE"]
    )

    pagination = flask_paginate.Pagination(
        page=page,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        error_out=False,
        total=len(schedules_metadata.keys()),
        items=schedules_metadata.keys(),
    )
    return flask.render_template(
        "download_schedules.html", pagination=pagination, data=schedules_result,
    )