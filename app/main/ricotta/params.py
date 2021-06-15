from app.imports.runtime import *
from app.main import main


@main.route("/ricotta_params", methods=["GET"])
@flask_login.login_required
def ricotta_params():
    return flask.render_template("ricotta/params.html")
