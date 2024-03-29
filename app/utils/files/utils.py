import json
import os
import pickle
import shutil

import flask
import openpyxl
import pycel

from utils_ak.os import makedirs


def cast_dynamic_fn(date, folder, basename):
    return os.path.join(flask.current_app.config["DYNAMIC_DIR"], date, folder, basename)


def create_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_file_dir(data, filename, date, folder, data_type="xlsx"):
    fn = cast_dynamic_fn(date, folder, filename)
    makedirs(fn)

    if data_type == "xlsx":
        data.save(fn)
    elif data_type == "csv":
        data.to_csv(fn, index=False, sep=";")
    elif data_type == "json":
        mode = "a" if os.path.exists(fn) else "w"
        with open(fn, mode) as outfile:
            json.dump(data, outfile)
    elif data_type == "pickle":
        with open(fn, "wb") as outfile:
            pickle.dump(data, outfile)


def save_boiling_plan(*args, **kwargs):
    save_file_dir(*args, **kwargs, folder=flask.current_app.config["BOILING_PLAN_FOLDER"])


def save_request(*args, **kwargs):
    save_file_dir(*args, **kwargs, folder=flask.current_app.config["REQUEST_FOLDER"])


def save_schedule(*args, **kwargs):
    save_file_dir(*args, **kwargs, folder=flask.current_app.config["SCHEDULE_FOLDER"])


def save_schedule_task(*args, **kwargs):
    save_file_dir(*args, **kwargs, folder=flask.current_app.config["TASK_FOLDER"], data_type="csv")


def save_schedule_dict(*args, **kwargs):
    save_file_dir(*args, **kwargs, folder=flask.current_app.config["SCHEDULE_DICT_FOLDER"], data_type="pickle")


def move_boiling_file(date, old_filepath, old_filename, department=""):
    new_filename = "{} План по варкам {}.xlsx".format(old_filename.split(" ")[0], department)
    data_dir = os.path.join(
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["REQUEST_FOLDER"],
    )
    create_if_not_exists(data_dir)

    filepath = os.path.join(data_dir, new_filename)
    shutil.copyfile(old_filepath, filepath)
    excel_compiler = pycel.ExcelCompiler(filepath)
    wb_data_only = openpyxl.load_workbook(filename=filepath, data_only=True)
    wb = openpyxl.load_workbook(filename=filepath)
    return excel_compiler, wb, wb_data_only, new_filename, filepath


def create_dir(date, folder):
    dir = os.path.join(flask.current_app.config["DYNAMIC_DIR"], date, folder)
    create_if_not_exists(dir)
    return dir


def move_to_approved(date, file_name):
    old_dir = os.path.join(
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["SCHEDULE_FOLDER"],
        file_name,
    )
    new_dir = os.path.join(
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["APPROVED_FOLDER"],
    )
    create_if_not_exists(new_dir)

    shutil.copyfile(old_dir, os.path.join(new_dir, file_name))
    return new_dir


def move_to_approved_pickle(date, file_name):
    old_dir = os.path.join(
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["SCHEDULE_DICT_FOLDER"],
        file_name,
    )
    new_dir = os.path.join(
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["APPROVED_FOLDER"],
    )
    create_if_not_exists(new_dir)
    if os.path.exists(old_dir):
        shutil.copyfile(old_dir, os.path.join(new_dir, file_name))
    return new_dir


def delete_from_approved_pickle(date, file_name):
    pickle_dir = os.path.join(
        flask.current_app.config["DYNAMIC_DIR"], date, flask.current_app.config["APPROVED_FOLDER"], file_name
    )
    if os.path.exists(pickle_dir):
        os.remove(pickle_dir)
