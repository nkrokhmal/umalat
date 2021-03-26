from flask import url_for, render_template
from werkzeug.utils import redirect
from .. import main
from ... import db
from .forms import LineForm
from ...models import MozzarellaLine


@main.route("/mozzarella/get_line", methods=["GET", "POST"])
def get_line():
    lines = db.session.query(MozzarellaLine).all()
    return render_template(
        "mozzarella/get_line.html", lines=lines, endpoints=".get_line"
    )


@main.route("/mozzarella/edit_line/<int:line_id>", methods=["GET", "POST"])
def edit_line(line_id):
    form = LineForm()
    line = db.session.query(MozzarellaLine).get_or_404(line_id)
    if form.validate_on_submit() and line is not None:
        line.name = form.name.data
        line.pouring_time = form.pouring_time.data
        line.serving_time = form.serving_time.data
        line.chedderization_time = form.chedderization_time.data
        line.melting_speed = form.melting_speed.data
        db.session.commit()

        flash("Параметры линии успешно изменены", "success")
        return redirect(url_for(".get_line"))

    form.name.data = line.name
    form.pouring_time.data = line.pouring_time
    form.serving_time.data = line.serving_time
    form.chedderization_time.data = line.chedderization_time
    form.melting_speed.data = line.melting_speed

    return render_template("mozzarella/edit_line.html", form=form, line_id=line.id)
