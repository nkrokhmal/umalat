import os
from itertools import groupby
from collections import OrderedDict
import flask_paginate

from app.imports.runtime import *
from app.main import main


def get_department(filename):
    filename_without_ext = filename.split('.')[0]
    return "моцарелла" if len(filename_without_ext.split(' ')) < 3 else filename_without_ext.split(' ')[-1]


def get_metadata(data, offset=0, per_page=10):
    keys = list(data.keys())[offset: offset + per_page]
    result = OrderedDict((key, data[key]) for key in keys if key in data)
    return OrderedDict(sorted(result.items(), reverse=True))


@main.route("/download_schedules/<int:page>", methods=["GET"])
def download_schedules(page):
    schedules_path = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["SCHEDULE_PLAN_FOLDER"],
    )
    schedule_task_path = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["TOTAL_SCHEDULE_TASK_FOLDER"],
    )

    schedules_filenames = os.listdir(schedules_path)
    schedules_task_filenames = os.listdir(schedule_task_path)
    schedules_metadata = {}

    for filename in schedules_filenames:
        date = filename.split(' ')[0]
        if date in schedules_metadata.keys():
            department = get_department(filename)
            if department not in schedules_metadata[date].keys():
                schedules_metadata[date][department] = filename
        else:
            schedules_metadata[date] = {}
            schedules_metadata[date][get_department(filename)] = filename

    for filename in schedules_task_filenames:
        date = filename.split('.')[0]
        if date in schedules_metadata.keys():
            department = "task"
            schedules_metadata[date][department] = filename

        else:
            schedules_metadata[date] = {}
            schedules_metadata[date]["task"] = filename

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