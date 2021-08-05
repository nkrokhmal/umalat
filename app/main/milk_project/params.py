from app.imports.runtime import *
from app.main import main


@main.route("/milk_project_params", methods=["GET"])
@flask_login.login_required
def milk_project_params():
    return flask.render_template("milk_project/params.html")

