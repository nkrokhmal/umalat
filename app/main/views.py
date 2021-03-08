from flask import (
    session,
    url_for,
    render_template,
    flash,
    request,
    make_response,
    send_from_directory,
    request,
)
from flask import jsonify
from werkzeug.utils import redirect
from . import main
from .errors import internal_error
from .. import db
from ..models_new import SKU, Boiling, Line, Termizator, Packer, Department
import pandas as pd
from io import BytesIO
import os
from datetime import datetime


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/get_general_params")
def get_general_params():
    lines = db.session.query(Line).all()
    packers = db.session.query(Packer).all()
    termizators = db.session.query(Termizator).all()
    departments = db.session.query(Department).all()
    return render_template(
        "get_general_params.html",
        lines=lines,
        packers=packers,
        termizators=termizators,
        departments=departments,
    )


@main.route("/get_packings/<int:boiling_id>", methods=["GET", "POST"])
def get_packings(boiling_id):
    pass


@main.route("/process_request", methods=["GET", "POST"])
def process_request():
    pass


@main.route("/get_lines", methods=["GET", "POST"])
def get_lines():
    lines = db.session.query(Line).all()
    return jsonify([x.serialize() for x in lines])


@main.route("/get_packer", methods=["GET", "POST"])
def get_packer():
    packers = db.session.query(Packer).all()
    return jsonify([x.serialize() for x in packers])


@main.route("//.", methods=["GET", "POST"])
def get_termizator():
    termizator = db.session.query(Termizator).all()
    return jsonify([x.serialize() for x in termizator])


@main.route("/get_department", methods=["GET", "POST"])
def get_department():
    departments = db.session.query(Department).all()
    return jsonify([x.serialize() for x in departments])


@main.route("/data/<path:path>")
def send_js(path):
    return send_from_directory("data", path)
