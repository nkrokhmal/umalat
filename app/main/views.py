from flask import session, url_for, render_template, flash, request, make_response, send_from_directory, request
from flask import jsonify
from werkzeug.utils import redirect
from . import main
from .. import db
from .. utils.excel_client import *
from .forms import PouringProcessForm, BoilingForm, RequestForm
from ..models import SKU, Boiling, GlobalPouringProcess, Melting, Pouring, Line, Termizator, Packer,\
    Departmenent
import pandas as pd
from io import BytesIO
import os
from datetime import datetime


@main.route('/')
def index():
    lines = db.session.query(Line).all()
    packers = db.session.query(Packer).all()
    termizators = db.session.query(Termizator).all()
    departments = db.session.query(Departmenent).all()
    return render_template('index.html', lines=lines, packers=packers, termizators=termizators, departments=departments)


@main.route('/get_packings/<int:boiling_id>', methods=['GET', 'POST'])
def get_packings(boiling_id):
    pass


@main.route('/process_request', methods=['GET', 'POST'])
def process_request():
    pass


@main.route('/get_lines', methods=['GET', 'POST'])
def get_lines():
    lines = db.session.query(Line).all()
    return jsonify([x.serialize() for x in lines])


@main.route('/get_packer', methods=['GET', 'POST'])
def get_packer():
    packers = db.session.query(Packer).all()
    return jsonify([x.serialize() for x in packers])


@main.route('/get_termizator', methods=['GET', 'POST'])
def get_termizator():
    termizator = db.session.query(Termizator).all()
    return jsonify([x.serialize() for x in termizator])


@main.route('/get_department', methods=['GET', 'POST'])
def get_department():
    departments = db.session.query(Departmenent).all()
    return jsonify([x.serialize() for x in departments])


@main.route('/data/<path:path>')
def send_js(path):
    return send_from_directory('data', path)


