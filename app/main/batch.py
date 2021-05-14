from app.imports.runtime import *
from app.main import main
from app.models import Department, BatchNumber


@main.route("/get_last_batch", methods=["POST", "GET"])
def download_boiling_plan(file_name):
    departments = db.session.query()
    # return response