from flask import url_for, render_template
from werkzeug.utils import redirect
from .. import main
from ... import db
from .forms import LineForm
from ...models import RicottaLine


@main.route("/ricotta/get_line", methods=["GET", "POST"])
def ricotta_get_line():
    lines = db.session.query(RicottaLine).all()
    return render_template(
        "ricotta/get_line.html", lines=lines, endpoints=".ricotta_get_line"
    )


@main.route("/ricotta/edit_line/<int:line_id>", methods=["GET", "POST"])
def ricotta_edit_line(line_id):
    form = LineForm()
    line = db.session.query(RicottaLine).get_or_404(line_id)
    if form.validate_on_submit() and line is not None:
        line.name = form.name.data
        line.input_ton = form.input_ton.data
        db.session.commit()
        return redirect(url_for(".ricotta_get_line"))

    form.name.data = line.name
    form.input_ton.data = line.input_ton

    return render_template("ricotta/edit_line.html", form=form, line_id=line.id)
