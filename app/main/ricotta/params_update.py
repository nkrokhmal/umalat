import itertools

from pathlib import Path

import flask
import flask_login
import pandas as pd

from app.globals import db
from app.main import main
from app.main.ricotta.forms import UpdateParamsForm
from app.models.fill_db.fill_ricotta import RicottaFiller
from app.models.ricotta import RicottaBoiling, RicottaBoilingTechnology, RicottaSKU
from app.utils.flash_msgs import Action, department_msg


@main.route("/ricotta/update_params", methods=["POST", "GET"])
@flask_login.login_required
def ricotta_update_params():
    form = UpdateParamsForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        file = flask.request.files["input_file"]
        path = Path(flask.current_app.config["UPLOAD_TMP_FOLDER"]) / file.filename

        if file:
            file.save(path)

        df = pd.read_excel(path, index_col=0)
        filler = RicottaFiller()

        msg = filler.validate_params(df)
        if msg is not None:
            flask.flash(f"{department_msg(action=Action.ERROR)} {msg}", "warning")
            return flask.redirect(flask.url_for(".ricotta_update_params"))

        for obj in (RicottaSKU, RicottaBoiling, RicottaBoilingTechnology):
            for item in db.session.query(obj).all():
                db.session.delete(item)
            db.session.commit()

        for obj in itertools.chain(filler.fill_boiling_technologies(df), filler.fill_boiling(df), filler.fill_sku(df)):
            db.session.add(obj)
        db.session.commit()

        flask.flash(department_msg(action=Action.EDIT), "success")
        return flask.redirect(flask.url_for(".ricotta_params"))

    return flask.render_template("ricotta/update_params.html", form=form)


__all__ = [
    "ricotta_update_params",
]
