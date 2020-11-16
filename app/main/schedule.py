from flask import session, url_for, render_template, flash, request, make_response, current_app, request
from werkzeug.utils import redirect
from . import main
from .. import db
from .forms import ScheduleForm
from ..models import SKU


@main.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = ScheduleForm()
    if request.method == 'POST' and form.validate_on_submit():
        date = form.date.data
        file_bytes = request.files['input_file'].read()
        return render_template('schedule.html', form=form)
    return render_template('schedule.html', form=form)