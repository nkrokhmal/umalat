from app.imports.runtime import *
from app.main import main


@main.route("/butter_params", methods=["GET"])
@flask_login.login_required
def butter_params():
    return flask.render_template("butter/params.html")
