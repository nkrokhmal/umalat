from app.imports.runtime import *

from werkzeug.utils import redirect
import itertools
from app.main import main
from .forms import MilkProjectBoilingTechnologyForm
from app.models import MilkProjectBoilingTechnology, MilkProjectSKU


@main.route("/milk_project/get_boiling_technology", methods=["GET", "POST"])
@flask_login.login_required
def milk_project_get_boiling_technology():
    skus = db.session.query(MilkProjectSKU).all()
    boiling_technologies = [sku.made_from_boilings[0].boiling_technologies for sku in skus]
    boiling_technologies = set(list(itertools.chain(*boiling_technologies)))
    return flask.render_template(
        "milk_project/get_boiling_technology.html",
        boiling_technologies=boiling_technologies,
        endpoints=".milk_project_get_boiling_technology",
    )


@main.route(
    "/milk_project/edit_boiling_technology/<int:boiling_technology_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def milk_project_edit_boiling_technology(boiling_technology_id):
    form = MilkProjectBoilingTechnologyForm()
    boiling_technology = db.session.query(MilkProjectBoilingTechnology).get_or_404(
        boiling_technology_id
    )
    if form.validate_on_submit() and boiling_technology is not None:
        boiling_technology.name = form.name.data
        boiling_technology.water_collecting_time = form.water_collecting_time.data
        boiling_technology.mixture_collecting_time = form.mixture_collecting_time.data
        boiling_technology.processing_time = form.processing_time.data
        boiling_technology.red_time = form.red_time.data

        db.session.commit()
        flask.flash("Параметры технологии успешно изменены", "success")
        return redirect(flask.url_for(".milk_project_get_boiling_technology"))

    form.name.data = boiling_technology.name
    form.water_collecting_time.data = boiling_technology.water_collecting_time
    form.mixture_collecting_time.data = boiling_technology.mixture_collecting_time
    form.processing_time.data = boiling_technology.processing_time
    form.red_time.data = boiling_technology.red_time

    return flask.render_template(
        "milk_project/edit_boiling_technology.html",
        form=form,
        boiling_technology_id=boiling_technology.id,
    )
