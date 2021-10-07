from collections import OrderedDict
import flask_paginate
from app.utils.files.update import update_data_structure
from app.imports.runtime import *
from app.main import main


def get_department(filename, default_mozzarella=True):
    filename_without_ext = filename.split('.')[0]
    if default_mozzarella:
        return "моцарелла" if len(filename_without_ext.split(' ')) < 3 else filename_without_ext.split(' ')[-1]
    else:
        return filename_without_ext.split(' ')[-1]


def get_department_task(filename):
    filename_without_ext = filename.split('.')[0]
    result = ' '.join(filename_without_ext.split(' ')[1:]).lower()
    return "default" if result == "" else result


def get_metadata(data, offset=0, per_page=10):
    keys = list(data.keys())[offset: offset + per_page]
    result = OrderedDict((key, data[key]) for key in keys if key in data)
    return OrderedDict(sorted(result.items(), reverse=True))


def is_approved(filename, date):
    return os.path.exists(
        os.path.join(
            flask.current_app.config['DYNAMIC_DIR'],
            date,
            flask.current_app.config["APPROVED_FOLDER"],
            filename,
        )
    )


@main.route("/update_data", methods=["GET"])
def update_data():
    update_data_structure(flask.current_app.config["BOILING_PLAN_FOLDER"])
    update_data_structure("schedule_plan")
    update_data_structure("schedule_task")
    response = flask.jsonify({"message": "Ok"})
    response.status_code = 200
    return response


@main.route("/download_contour_washer_history/<int:page>", methods=["GET"])
@flask_login.login_required
def download_contour_washer_history(page):
    date_dirs = next(os.walk(flask.current_app.config["DYNAMIC_DIR"]))[1]
    cw_metadata = {}

    def is_date(string):
        try:
            _ = datetime.strptime(string, flask.current_app.config["DATE_FORMAT"])
            return True
        except:
            return False

    for date_dir in date_dirs:
        if is_date(date_dir):
            cw_dir = os.path.join(
                flask.current_app.config["DYNAMIC_DIR"],
                date_dir,
                flask.current_app.config["APPROVED_FOLDER"])
            if os.path.exists(cw_dir):
                cw_filenames = os.listdir(cw_dir)
                if cw_filenames:
                    cw_metadata[date_dir] = {}
                    for cw_filename in cw_filenames:
                        if "контурные мойки.xlsx" in cw_filename:
                            cw_metadata[date_dir] = {}
                            cw_metadata[date_dir]['filename'] = cw_filename

    cw_metadata = OrderedDict(sorted(cw_metadata.items(), reverse=True))
    cw_result = get_metadata(
        cw_metadata,
        offset=(page - 1) * flask.current_app.config["SKU_PER_PAGE"],
        per_page=flask.current_app.config["SKU_PER_PAGE"]
    )

    pagination = flask_paginate.Pagination(
        page=page,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        error_out=False,
        total=len(cw_metadata.keys()),
        items=cw_metadata.keys(),
    )
    return flask.render_template(
        "history/download_contour_washers.html", pagination=pagination, data=cw_result,
    )


@main.route("/download_boiling_plans/<int:page>", methods=["GET"])
@flask_login.login_required
def download_boiling_plans(page):
    date_dirs = next(os.walk(flask.current_app.config["DYNAMIC_DIR"]))[1]
    bp_metadata = {}

    def is_date(string):
        try:
            _ = datetime.strptime(string, flask.current_app.config["DATE_FORMAT"])
            return True
        except:
            return False

    for date_dir in date_dirs:
        if is_date(date_dir):
            bp_dir = os.path.join(
                flask.current_app.config["DYNAMIC_DIR"],
                date_dir,
                flask.current_app.config["BOILING_PLAN_FOLDER"])
            if os.path.exists(bp_dir):
                bp_filenames = os.listdir(bp_dir)
                if bp_filenames:
                    bp_metadata[date_dir] = {}
                    for bp_filename in bp_filenames:
                        department = get_department(bp_filename)
                        if department not in bp_metadata[date_dir].keys():
                            bp_metadata[date_dir][department] = {}
                            bp_metadata[date_dir][department]['filename'] = bp_filename

    bp_metadata = OrderedDict(sorted(bp_metadata.items(), reverse=True))
    bp_result = get_metadata(
        bp_metadata,
        offset=(page - 1) * flask.current_app.config["SKU_PER_PAGE"],
        per_page=flask.current_app.config["SKU_PER_PAGE"]
    )

    pagination = flask_paginate.Pagination(
        page=page,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        error_out=False,
        total=len(bp_metadata.keys()),
        items=bp_metadata.keys(),
    )
    return flask.render_template(
        "history/download_boiling_plans.html", pagination=pagination, data=bp_result,
    )


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
            schedule_dir = os.path.join(
                flask.current_app.config["DYNAMIC_DIR"],
                date_dir,
                flask.current_app.config["SCHEDULE_FOLDER"])
            if os.path.exists(schedule_dir):
                schedules_filenames = os.listdir(schedule_dir)
                if schedules_filenames:
                    schedules_metadata[date_dir] = {}
                    for schedules_filename in schedules_filenames:
                        department = get_department(schedules_filename)
                        if department not in schedules_metadata[date_dir].keys():
                            schedules_metadata[date_dir][department] = {}
                            schedules_metadata[date_dir][department]['filename'] = schedules_filename
                            schedules_metadata[date_dir][department]['is_approved'] = is_approved(schedules_filename, date_dir)

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
        "history/download_schedules.html", pagination=pagination, data=schedules_result,
    )


@main.route("/download_schedule_tasks/<int:page>", methods=["GET"])
@flask_login.login_required
def download_schedule_tasks(page):
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
            schedule_dir = os.path.join(
                flask.current_app.config["DYNAMIC_DIR"],
                date_dir,
                flask.current_app.config["TASK_FOLDER"])
            if os.path.exists(schedule_dir):
                schedules_filenames = os.listdir(schedule_dir)
                if schedules_filenames:
                    schedules_metadata[date_dir] = {}
                    for schedules_filename in schedules_filenames:
                        department = get_department_task(schedules_filename)
                        if department not in schedules_metadata[date_dir].keys():
                            schedules_metadata[date_dir][department] = {}
                            schedules_metadata[date_dir][department]['filename'] = schedules_filename

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
        "history/download_schedule_tasks.html", pagination=pagination, data=schedules_result,
    )

