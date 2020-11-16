from flask import session, url_for, render_template, flash, request, make_response, current_app, request
from werkzeug.utils import redirect
from . import main
from .. import db
from .forms import BoilingForm
from ..models import Boiling, Pouring, Melting


@main.route('/get_boiling', methods=['GET', 'POST'])
def get_boiling():
    boilings = db.session.query(Boiling).all()
    return render_template('get_boiling.html', boilings=boilings, endpoints='.get_boiling')


@main.route('/delete_boiling/<int:boiling_id>', methods=['DELETE'])
def delete_boiling(boiling_id):
    boiling_process = db.session.query(Boiling).get_or_404(boiling_id)
    if boiling_process:
        db.session.delete(boiling_process)
        db.session.commit()
    return redirect(url_for('.get_boiling'))


@main.route('/edit_boiling/<int:boiling_id>',  methods=['GET', 'POST'])
def edit_boiling(boiling_id):
    form = BoilingForm()
    with db.session.no_autoflush:
        boiling_process = db.session.query(Boiling).get_or_404(boiling_id)
        if form.validate_on_submit() and boiling_process is not None:
            boiling_process.percent = form.percent.data
            boiling_process.priority = form.priority.data
            boiling_process.is_lactose = form.is_lactose.data
            boiling_process.ferment = dict(form.ferment.choices).get(form.ferment.data)

            pouring_process = Pouring(
                pouring_time=form.pouring_time.data,
                soldification_time=form.soldification_time.data,
                cutting_time=form.cutting_time.data,
                pouring_off_time=form.pouring_off_time.data,
                extra_time=form.extra_time.data
            )
            boiling_process.pourings = pouring_process

            melting_process = Melting(
                serving_time=form.serving_time.data,
                melting_time=form.melting_time.data,
                speed=form.speed.data,
                first_cooling_time=form.first_cooling_time.data,
                second_cooling_time=form.second_cooling_time.data,
                salting_time=form.salting_time.data
            )
            boiling_process.meltings = melting_process

            db.session.commit()
            return redirect(url_for('.get_boiling'))
        for key, value in dict(form.ferment.choices).items():
            if value == boiling_process.ferment:
                form.ferment.default = key
                form.process()
        form.percent.data = boiling_process.percent
        form.priority.data = boiling_process.priority
        form.is_lactose.data = boiling_process.is_lactose


        if boiling_process.pourings is not None:
            form.pouring_time.data = boiling_process.pourings.pouring_time
            form.soldification_time.data = boiling_process.pourings.soldification_time
            form.cutting_time.data = boiling_process.pourings.cutting_time
            form.pouring_off_time.data = boiling_process.pourings.pouring_off_time
            form.extra_time.data = boiling_process.pourings.extra_time
        if boiling_process.meltings is not None:
            form.serving_time.data = boiling_process.meltings.serving_time
            form.melting_time.data = boiling_process.meltings.melting_time
            form.speed.data = boiling_process.meltings.speed
            form.first_cooling_time.data = boiling_process.meltings.first_cooling_time
            form.second_cooling_time.data = boiling_process.meltings.second_cooling_time
            form.salting_time.data = boiling_process.meltings.salting_time

        return render_template('edit_boiling.html', form=form)


@main.route('/add_boiling', methods=['GET', 'POST'])
def add_boilings():
    form = BoilingForm()
    if form.validate_on_submit():
        boiling = Boiling(
            percent=form.percent.data,
            priority=form.priority.data,
            is_lactose=form.is_lactose.data
        )
        pouring_process = Pouring(
            pouring_time=form.pouring_time.data,
            soldification_time=form.soldification_time.data,
            cutting_time=form.cutting_time.data,
            pouring_off_time=form.pouring_off_time.data,
            extra_time=form.extra_time.data
        )
        melting_process = Melting(
            serving_time=form.serving_time.data,
            melting_time=form.melting_time.data,
            speed=form.speed.data,
            first_cooling_time=form.first_cooling_time.data,
            second_cooling_time=form.second_cooling_time.data,
            salting_time=form.salting_time.data
        )
        boiling.pourings = pouring_process
        boiling.meltings = melting_process
        db.session.add(boiling)
        db.session.commit()
        return redirect(url_for('.get_boiling'))
    return render_template('add_boiling.html', form=form)