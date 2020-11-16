from flask import url_for, render_template
from werkzeug.utils import redirect
from . import main
from .. import db
from .forms import PouringProcessForm
from ..models import GlobalPouringProcess


@main.route('/add_pouring_process', methods=['POST', 'GET'])
def add_pouring_process():
    form = PouringProcessForm()
    if form.validate_on_submit():
        pouring_process = GlobalPouringProcess(
            pouring_time=form.pouring_time.data
        )
        db.session.add(pouring_process)
        db.session.commit()
        return redirect(url_for('.get_pouring_process'))
    return render_template('add_pouring_process.html', form=form)


@main.route('/get_pouring_process')
def get_pouring_process():
    pouring_processes = db.session.query(GlobalPouringProcess).all()
    return render_template('get_pouring_process.html', pouring_processes=pouring_processes, endopoints='.get_pouring_process')


@main.route('/edit_pouring_process/<int:id>', methods=['GET', 'POST'])
def edit_pouring_process(id):
    form = PouringProcessForm()
    pouring_process = db.session.query(GlobalPouringProcess).get_or_404(id)
    if form.validate_on_submit() and pouring_process is not None:
        pouring_process.pouring_time = form.pouring_time.data
        db.session.commit()
        return redirect(url_for('.get_pouring_process'))
    form.pouring_time.data = pouring_process.pouring_time
    return render_template('edit_pouring_process.html', form=form)