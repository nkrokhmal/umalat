import itertools

from pathlib import Path

import flask
import flask_login
import pandas as pd

from app.globals import db
from app.main import main
from app.main.mascarpone.forms import UpdateParamsForm
from app.models.fill_db.fill_mascarpone import fill_boiling_technologies, fill_boilings, fill_sku, validate_params
from app.models.mascarpone import MascarponeBoiling, MascarponeBoilingTechnology, MascarponeSKU
from app.utils.flash_msgs import Action, department_msg


@main.route("/mascarpone/update_params", methods=["POST", "GET"])
@flask_login.login_required
def mascarpone_update_params():
    form = UpdateParamsForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        file = flask.request.files["input_file"]
        path = Path(flask.current_app.config["UPLOAD_TMP_FOLDER"]) / file.filename

        if file:
            file.save(path)

        df = pd.read_excel(path, index_col=0)
        is_valid, msg = validate_params(df)
        if not is_valid:
            flask.flash(f"{department_msg(action=Action.ERROR)} {msg}", "warning")
            return flask.redirect(flask.url_for(".mascarpone_update_params"))

        for obj in (MascarponeSKU, MascarponeBoiling, MascarponeBoilingTechnology):
            for item in db.session.query(obj).all():
                db.session.delete(item)
            db.session.commit()

        for obj in itertools.chain(fill_boiling_technologies(df), fill_boilings(df), fill_sku(df)):
            db.session.add(obj)
        db.session.commit()

        flask.flash(department_msg(action=Action.EDIT), "success")
        return flask.redirect(flask.url_for(".mascarpone_params"))

    return flask.render_template("mascarpone/update_params.html", form=form)


__all__ = [
    "mascarpone_update_params",
]
