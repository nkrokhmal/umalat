from werkzeug.utils import redirect

from app.enum import DepartmentName
from app.imports.runtime import *
from app.main import main
from app.models import Department, Washer

from .forms import WasherForm


@main.route("/mozzarella/get_washer", methods=["GET", "POST"])
@flask_login.login_required
def get_washer():
    washers = db.session.query(Washer).join(Department).filter(Department.name == DepartmentName.MOZZARELLA).all()
    return flask.render_template("mozzarella/get_washer.html", washers=washers, endpoints=".get_washer")


@main.route("/mozzarella/edit_washer/<int:washer_id>", methods=["GET", "POST"])
@flask_login.login_required
def edit_washer(washer_id):
    form = WasherForm()
    washer = db.session.query(Washer).get_or_404(washer_id)
    if form.validate_on_submit() and washer is not None:
        washer.name = form.name.data
        washer.time = form.time.data
        db.session.commit()
        flask.flash("Параметры мойки успешно изменены", "success")
        return redirect(flask.url_for(".get_washer"))

    form.name.data = washer.name
    form.time.data = washer.time

    return flask.render_template("mozzarella/edit_washer.html", form=form, washer_id=washer.id)
