from app.imports.runtime import *
from app.main import main


@main.route("/milkproject_params", methods=["GET"])
@flask_login.login_required
def milkproject_params():
    return flask.render_template("milkproject/params.html")

