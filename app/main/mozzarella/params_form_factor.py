from app.imports.runtime import *

from app.main import main
from app.models import MozzarellaFormFactor
from app.utils.features.form_utils import *
from app.enum import LineName

from .forms import FormFactorForm


@main.route("/mozzarella/get_form_factor", methods=["GET", "POST"])
def get_form_factor():
    form_factors = db.session.query(MozzarellaFormFactor).all()
    water_form_factors = sorted(
        [
            ff
            for ff in form_factors
            if (ff.name != "Масса")
            and ("Терка" not in ff.name)
            and (ff.line.name == LineName.WATER)
        ],
        key=lambda ff: ff.name,
    )
    salt_form_factors = sorted(
        [
            ff
            for ff in form_factors
            if (ff.name != "Масса")
            and ("Терка" not in ff.name)
            and (ff.line.name == LineName.SALT)
        ],
        key=lambda ff: ff.name,
    )
    return render_template(
        "mozzarella/get_form_factor.html",
        water_form_factors=water_form_factors,
        salt_form_factors=salt_form_factors,
        endpoints=".get_form_factor",
    )


@main.route(
    "/mozzarella/edit_form_factor/<int:form_factor_id>", methods=["GET", "POST"]
)
def edit_form_factor(form_factor_id):
    form = FormFactorForm()
    form_factor = db.session.query(MozzarellaFormFactor).get_or_404(form_factor_id)
    if form.validate_on_submit() and form_factor is not None:
        form_factor.default_cooling_technology.first_cooling_time = (
            form.first_cooling_time.data
        )
        form_factor.default_cooling_technology.second_cooling_time = (
            form.second_cooling_time.data
        )
        form_factor.default_cooling_technology.salting_time = form.salting_time.data
        db.session.commit()

        flash("Параметры форм фактора успешно изменены", "success")
        return redirect(url_for(".get_form_factor"))

    form.name.data = form_factor.name
    form.first_cooling_time.data = (
        form_factor.default_cooling_technology.first_cooling_time
    )
    form.second_cooling_time.data = (
        form_factor.default_cooling_technology.second_cooling_time
    )
    form.salting_time.data = form_factor.default_cooling_technology.salting_time
    form.line.data = form_factor.line.name

    return render_template(
        "mozzarella/edit_form_factor.html", form=form, form_factor_id=form_factor.id
    )
