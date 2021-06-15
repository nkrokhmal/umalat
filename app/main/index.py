import flask

from app.imports.runtime import *
from app.main import main


@main.route("/")
def index():
    if not flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('.login'))
    else:
        return flask.render_template("index.html")
