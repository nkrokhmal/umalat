import flask

from app.imports.runtime import *
from app.main import main


@main.route("/")
def index():
    if flask.current_app.config['TESTING']:
        return flask.render_template("index.html")
    else:
        if not flask_login.current_user.is_authenticated:
            return flask.redirect(flask.url_for('.login'))
        else:
            return flask.render_template("index.html")
