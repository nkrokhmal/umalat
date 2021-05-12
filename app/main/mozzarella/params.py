from app.imports.runtime import *
from app.main import main


@main.route("/mozzarella_params", methods=["GET"])
def mozzarella_params():
    return render_template("mozzarella/params.html")
