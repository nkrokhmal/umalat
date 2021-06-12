from app.imports.runtime import *
from app.main import main


@main.route("/mozzarella_params", methods=["GET"])
@flask_login.login_required
def mozzarella_params():
    return flask.render_template("mozzarella/params.html")
