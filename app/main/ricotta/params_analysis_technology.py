from app.imports.runtime import *

from werkzeug.utils import redirect

from app.main import main
from app.models import RicottaAnalysisTechnology

from .forms import AnalysisForm


@main.route("/ricotta/get_analysis_technology", methods=["GET", "POST"])
@flask_login.login_required
def ricotta_get_analysis_technology():
    analysis_technologies = db.session.query(RicottaAnalysisTechnology).all()
    return flask.render_template(
        "ricotta/get_analysis_technology.html",
        boiling_technologies=analysis_technologies,
        endpoints=".ricotta_get_analysis_technology",
    )


@main.route(
    "/ricotta/edit_analysis_technology/<int:analysis_technology_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def ricotta_edit_analysis_technology(analysis_technology_id):
    form = AnalysisForm()
    analysis_technology = db.session.query(RicottaAnalysisTechnology).get_or_404(
        analysis_technology_id
    )
    if form.validate_on_submit() and analysis_technology is not None:
        analysis_technology.preparation_time = form.preparation_time.data
        analysis_technology.analysis_time = form.analysis_time.data
        analysis_technology.pumping_time = form.pumping_time.data

        db.session.commit()
        flask.flash("Параметры анализа технологии успешно изменены", "success")
        return redirect(flask.url_for(".ricotta_get_analysis_technology"))

    form.preparation_time.data = analysis_technology.preparation_time
    form.analysis_time.data = analysis_technology.analysis_time
    form.pumping_time.data = analysis_technology.pumping_time
    form.boiling_name.data = analysis_technology.boiling.to_str()

    return flask.render_template(
        "ricotta/edit_analysis_technology.html",
        form=form,
        analysis_technology_id=analysis_technology.id,
    )
