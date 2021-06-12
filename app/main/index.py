from app.imports.runtime import *
from app.main import main


@main.route("/")
@flask_login.login_required
def index():
    return flask.render_template("index.html")
