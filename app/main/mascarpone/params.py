from app.imports.runtime import *
from app.main import main


@main.route("/mascarpone_params", methods=["GET"])
def mascarpone_params():
    return flask.render_template("mascarpone/params.html")
