from flask import session, url_for, render_template, flash, request, make_response, current_app, request
from flask_restplus import abort
from werkzeug.utils import redirect
from . import main
from .. import db
from .forms import SKUForm, PouringProcessForm, BoilingForm, RequestForm
from ..models import SKU, Boiling, GlobalPouringProcess, MeltingProcess, PouringProcess
import pandas as pd
from io import BytesIO



@main.route('/')
def index():
    return render_template('index.html')


@main.route('/add_sku', methods=['POST', 'GET'])
def add_sku():
    form = SKUForm()
    if form.validate_on_submit():
        sku = SKU(
            name=form.name.data,
            size=form.size.data,
            speed=form.speed.data,
            packing_reconfiguration=form.packing_reconfiguration.data,
            packing_reconfiguration_format=form.packing_reconfiguration_format.data,
            boiling_id=[x.id for x in form.boilings if
                        x.percent == dict(form.percent.choices).get(form.percent.data) and
                        x.is_lactose == dict(form.is_lactose.choices).get(form.is_lactose.data)][0],
            packing_id=[x.id for x in form.packings if
                        x.name == dict(form.packing.choices).get(form.packing.data)][0]
        )
        db.session.add(sku)
        db.session.commit()
        return redirect(url_for('.get_sku'))
    return render_template('add_sku.html', form=form)


@main.route('/get_sku', methods=['GET'])
def get_sku():
    form = SKUForm()
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(SKU) \
        .order_by(SKU.name) \
        .paginate(
            page, per_page=current_app.config['SKU_PER_PAGE'],
            error_out=False
    )
    skus = pagination.items
    return render_template('get_sku.html', form=form, skus=skus, paginations=pagination, endopoints='.get_sku')


@main.route('/edit_sku/<int:sku_id>', methods=['GET', 'POST'])
def edit_sku(sku_id):
    form = SKUForm()
    sku = db.session.query(SKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        sku.name = form.name.data
        sku.size = form.size.data
        sku.speed = form.speed.data
        sku.packing_id = [x.id for x in form.packings if
                          x.name == dict(form.packing.choices).get(form.packing.data)][0]
        sku.packing_reconfiguration = form.packing_reconfiguration.data
        sku.packing_reconfiguration_format = form.packing_reconfiguration_format.data
        sku.boiling_id = [x.id for x in form.boilings if
                        x.percent == dict(form.percent.choices).get(form.percent.data) and
                        x.is_lactose == dict(form.is_lactose.choices).get(form.is_lactose.data)][0]
        db.session.commit()
        return redirect(url_for('.get_sku'))
    form.name.data = sku.name
    form.size.data = sku.size
    form.speed.data = sku.speed
    form.percent.data = sku.boiling.percent
    form.is_lactose.data = sku.boiling.is_lactose
    form.packing_reconfiguration.data = sku.packing_reconfiguration
    form.packing_reconfiguration_format.data = sku.sku.packing_reconfiguration_format
    return render_template('edit_sku.html', form=form)


@main.route('/delete_sku/<int:sku_id>', methods=['DELETE'])
def delete_sku(sku_id):
    sku = db.session.query(SKU).get_or_404(sku_id)
    if sku:
        db.session.delete(sku)
        db.session.commit()
    return redirect(url_for('.get_sku'))


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

            pouring_process = PouringProcess(
                pouring_time=form.pouring_time.data,
                soldification_time=form.soldification_time.data,
                cutting_time=form.cutting_time.data,
                pouring_off_time=form.pouring_off_time.data,
                extra_time=form.extra_time.data
            )
            boiling_process.pourings = pouring_process

            melting_process = MeltingProcess(
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
        pouring_process = PouringProcess(
            pouring_time=form.pouring_time.data,
            soldification_time=form.soldification_time.data,
            cutting_time=form.cutting_time.data,
            pouring_off_time=form.pouring_off_time.data,
            extra_time=form.extra_time.data
        )
        melting_process = MeltingProcess(
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


@main.route('/get_packings/<int:boiling_id>', methods=['GET', 'POST'])
def get_packings(boiling_id):
    pass


@main.route('/parse_request', methods=['GET', 'POST'])
def parse_request():
    form = RequestForm()
    if request.method == 'POST' and form.validate_on_submit():
        file_bytes = request.files['input_file'].read()
        df = pd.read_excel(BytesIO(file_bytes), index_col=0)
        df.columns = range(df.shape[1])
        df = df[df.loc['Дата выработки продукции:'].dropna().index]
        df = df.loc[['Дата выработки продукции:',
                     'Заявлено всего, кг:',
                     'Фактические остатки на складах - Заявлено, кг:',
                     'Нормативные остатки, кг']].fillna(0)
        data = list(zip(*df.values.tolist()))
        return render_template('parse_request.html', data=data, form=form)
    data = None
    return render_template('parse_request.html', data=data, form=form)


# @main.route('/add_pouring_process', methods=['GET', 'POST'])
# def add_pouring_process():
#     pass
#
#
# @main.route('/delete_pouring_process/<int:pouring_process_id>', methods=['DELETE'])
# def delete_pouring_process(pouring_process_id):
#     pass
#
#
# @main.route('/edit_pouring_process/<int:pouring_process_id>', methods=['GET', 'POST'])
# def edit_pouring_process(pouring_process_id):
#     pass
#
#
# @main.route('/get_melting_process', methods=['GET', 'POST'])
# def get_melting_process():
#     pass
#
#
# @main.route('/add_melting_process', methods=['GET', 'POST'])
# def add_melting_process():
#     pass
#
#
# @main.route('/delete_melting_process/<int:melting_process_id>', methods=['DELETE'])
# def delete_melting_process(melting_process_id):
#     pass
#
#
# @main.route('/edit_melting_process/<int:melting_process_id>', methods=['GET', 'POST'])
# def edit_melting_process():
#     pass








# @main.route('/cheeses', methods=['GET', 'POST'])
# def cheeses():
#     page = request.args.get('page', 1, type=int)
#     pagination = db.session.query(Cheese)\
#         .order_by(Cheese.cheese_name)\
#         .paginate(
#             page, per_page=current_app.config['CHEESE_PER_PAGE'],
#             error_out=False
#     )
#     cheeses = pagination.items
#     return render_template('cheeses.html', cheeses=cheeses, pagination=pagination, endpoint='.cheeses')
#
#
# @main.route('/edit_cheese/<int:id>', methods=['GET', 'POST'])
# def edit_cheese(id):
#     form = CheeseForm()
#     cheese = db.session.query(Cheese).get_or_404(id)
#     print(cheese.cutting_time)
#     if form.validate_on_submit():
#         cheese.cheese_name = form.cheese_name.data
#         cheese.leaven_time = form.leaven_time.data
#         cheese.solidification_time = form.solidification_time.data
#         cheese.draining_time = form.draining_time.data
#         cheese.cutting_time = form.cutting_time.data
#         cheese.cheese_maker = db.session.query(CheeseMaker).get(form.cheese_maker.data)
#         db.session.add(cheese)
#         db.session.commit()
#         return redirect(url_for('.cheeses'))
#     form.cheese_name.data = cheese.cheese_name
#     form.leaven_time.data = cheese.leaven_time
#     form.solidification_time.data = cheese.solidification_time
#     form.cutting_time.data = cheese.cutting_time
#     form.draining_time.data = cheese.draining_time
#     form.cheese_maker.data = cheese.cheese_maker_id
#     return render_template('edit_cheese.html', form=form)
#
#
# @main.route('/delete_cheese/<int:id>', methods=['DELETE'])
# def delete_cheese(id):
#     cheese = db.session.query(Cheese).get_or_404(id)
#     if cheese:
#         db.session.delete(cheese)
#         db.session.commit()
#     return redirect(url_for('.cheeses'))
#
#
# @main.route('/add_cheese', methods=['GET', 'POST'])
# def add_cheese():
#     form = CheeseForm()
#     if form.validate_on_submit():
#         cheese = Cheese(
#             cheese_name=form.cheese_name.data,
#             leaven_time=form.leaven_time.data,
#             solidification_time=form.solidification_time.data,
#             cutting_time=form.cutting_time.data,
#             draining_time=form.draining_time.data,
#             cheese_maker=db.session.query(CheeseMaker).get(form.cheese_maker.data)
#         )
#         db.session.add(cheese)
#         db.session.commit()
#         return redirect(url_for('.cheeses'))
#     return render_template('add_cheese.html', form=form)
#
#
# @main.route('/cheese_makers', methods=['GET', 'POST'])
# def cheese_makers():
#     page = request.args.get('page', 1, type=int)
#     pagination = db.session.query(CheeseMaker)\
#         .order_by(CheeseMaker.cheese_maker_name)\
#         .paginate(
#         page, per_page=current_app.config['CHEESE_MAKER_PER_PAGE'],
#         error_out=False
#     )
#     cheese_makers = pagination.items
#     return render_template('cheese_makers.html', cheese_makers=cheese_makers)
#
#
# @main.route('/add_cheese_maker', methods=['GET', 'POST'])
# def add_cheese_maker():
#     form = CheeseMakerForm()
#     if form.validate_on_submit():
#         cheese_maker = CheeseMaker(
#             cheese_maker_name=form.cheese_maker_name.data
#         )
#         db.session.add(cheese_maker)
#         db.session.commit()
#         return redirect(url_for('.index'))
#     return render_template('add_cheese_maker.html', form=form)
#
#
# @main.route('/cheese_scheduler', methods=['GET', 'POST'])
# def cheese_scheduler():
#     return render_template('cheese_scheduler.html')
