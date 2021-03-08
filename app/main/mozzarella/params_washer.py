from flask import url_for, render_template
from werkzeug.utils import redirect
from .. import main
from ... import db
from .forms import WasherForm
from ...models import Washer, Department
from ...enum import DepartmentName


@main.route("/mozzarella/get_washer", methods=["GET", "POST"])
def get_washer():
    washers = (
        db.session.query(Washer)
        .join(Department)
        .filter(Department.name == DepartmentName.MOZZ)
        .all()
    )
    return render_template(
        "mozzarella/get_washer.html", washers=washers, endpoints=".get_washer"
    )


@main.route("/mozzarella/edit_washer/<int:washer_id>", methods=["GET", "POST"])
def edit_washer(washer_id):
    form = WasherForm()
    washer = db.session.query(Washer).get_or_404(washer_id)
    if form.validate_on_submit() and washer is not None:
        washer.name = form.name.data
        washer.time = form.time.data
        db.session.commit()
        return redirect(url_for(".get_washer"))

    form.name.data = washer.name
    form.time.data = washer.time

    return render_template(
        "mozzarella/edit_washer.html", form=form, washer_id=washer.id
    )
