from flask import url_for, render_template, flash
from werkzeug.utils import redirect
from .. import main
from ... import db
from .forms import AnalysisForm
from ...models import RicottaAnalysisTechnology


@main.route("/ricotta/get_analysis_technology", methods=["GET", "POST"])
def ricotta_get_analysis_technology():
    analysis_technologies = db.session.query(RicottaAnalysisTechnology).all()
    return render_template(
        "ricotta/get_analysis_technology.html",
        boiling_technologies=analysis_technologies,
        endpoints=".ricotta_get_analysis_technology",
    )


@main.route(
    "/ricotta/edit_analysis_technology/<int:analysis_technology_id>",
    methods=["GET", "POST"],
)
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
        flash("Варка успешно изменена!")
        print("Finished")
        return redirect(url_for(".ricotta_get_analysis_technology"))

    form.preparation_time.data = analysis_technology.preparation_time
    form.analysis_time.data = analysis_technology.analysis_time
    form.pumping_time.data = analysis_technology.pumping_time
    form.boiling_name.data = analysis_technology.boiling.to_str()

    return render_template(
        "ricotta/edit_analysis_technology.html",
        form=form,
        analysis_technology_id=analysis_technology.id,
    )
