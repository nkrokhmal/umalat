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
from .. import db
import pandas as pd
from io import BytesIO
import os
from datetime import datetime


@main.route("/")
def index():
    return render_template("index.html")
