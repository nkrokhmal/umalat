import flask
from app.imports.runtime import *
from app.main import main
from app.models import Department, BatchNumber


@main.route("/save_last_batches", methods=["GET"])
@flask_login.login_required
def save_last_batches():
    departments = db.session.query(Department).all()
    last_batches = []
    for department in departments:
        last_batch = db.session.query(BatchNumber)\
            .filter(BatchNumber.department_id == department.id)\
            .order_by(BatchNumber.datetime.desc())\
            .first()
        if last_batch:
            last_batches.append(last_batch.serialize())
    batch_number_path = os.path.join(flask.current_app.config["BATCH_NUMBERS_DIR"], "data.json")
    mode = 'a' if os.path.exists(batch_number_path) else 'w'
    with open(batch_number_path, mode) as file:
        file.truncate(0)
        json.dump(last_batches, file)
    response = flask.jsonify({"last_batches": last_batches})
    response.status_code = 200
    return response


@main.route("/upload_last_batches", methods=["GET", "POST"])
@flask_login.login_required
def upload_last_batches():
    batch_number_path = os.path.join(flask.current_app.config["BATCH_NUMBERS_DIR"], "data.json")
    if os.path.exists(batch_number_path):
        with open(batch_number_path) as json_file:
            last_batches = json.load(json_file)
            for department in last_batches:
                batch = BatchNumber(
                    datetime=datetime.strptime(department["datetime"], flask.current_app.config["DATE_FORMAT"]),
                    beg_number=department["beg_number"],
                    end_number=department["end_number"],
                    department_id=department["department_id"],
                )
                db.session.add(batch)
            db.session.commit()
    response = flask.jsonify({"status": "Ok"})
    response.status_code = 200
    return response
