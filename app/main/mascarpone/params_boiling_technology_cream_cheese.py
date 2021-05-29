from werkzeug.utils import redirect
from app.imports.runtime import *
from app.main import main
from app.models import CreamCheeseBoilingTechnology
from .forms import CreamCheeseBoilingTechnologyForm


@main.route("/mascarpone/get_boiling_technology_cream_cheese", methods=["GET", "POST"])
def mascarpone_get_boiling_technology_cream_cheese():
    boiling_technologies = db.session.query(CreamCheeseBoilingTechnology).all()
    return flask.render_template(
        "mascarpone/get_boiling_technology_cream_cheese.html",
        boiling_technologies=boiling_technologies,
        endpoints=".mascarpone_get_boiling_technology_cream_cheese",
    )


@main.route(
    "/mascarpone/edit_boiling_technology_cream_cheese/<int:boiling_technology_id>",
    methods=["GET", "POST"],
)
def mascarpone_edit_boiling_technology_cream_cheese(boiling_technology_id):
    form = CreamCheeseBoilingTechnologyForm()
    boiling_technology = db.session.query(CreamCheeseBoilingTechnology).get_or_404(
        boiling_technology_id
    )
    if form.validate_on_submit() and boiling_technology is not None:
        boiling_technology.name = form.name.data
        boiling_technology.cooling_time = form.cooling_time.data
        boiling_technology.separation_time = form.separation_time.data
        boiling_technology.salting_time = form.salting_time.data
        boiling_technology.p_time = form.p_time.data

        db.session.commit()
        flask.flash("Параметры технологии успешно изменены", "success")
        return redirect(flask.url_for(".mascarpone_get_boiling_technology_cream_cheese"))

    form.name.data = boiling_technology.name
    form.cooling_time.data = boiling_technology.cooling_time
    form.separation_time.data = boiling_technology.separation_time
    form.salting_time.data = boiling_technology.salting_time
    form.p_time.data = boiling_technology.p_time

    return flask.render_template(
        "mascarpone/edit_boiling_technology_cream_cheese.html",
        form=form,
        boiling_technology_id=boiling_technology.id,
    )
