from flask import session, url_for, render_template, flash, request, make_response, current_app
from flask_restplus import abort
from werkzeug.utils import redirect
from . import main
from .. import db
from .forms import SKUForm
from ..models import SKU, Boiling

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/add_sku', methods=['POST', 'GET'])
def add_sku():
    form = SKUForm()
    if form.validate_on_submit():
        print(form.boilings)
        print(form.percent.data)
        print(form.is_lactose.data)

        sku = SKU(
            name=form.name.data,
            size=form.size.data,
            boiling_id=[x.id for x in form.boilings if
                        x.percent == dict(form.percent.choices).get(form.percent.data) and
                        x.is_lactose == dict(form.is_lactose.choices).get(form.is_lactose.data)][0]
        )
        db.session.add(sku)
        db.session.commit()
        return redirect(url_for('.index'))
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
        sku.boiling_id = [x.id for x in form.boilings if
                        x.percent == dict(form.percent.choices).get(form.percent.data) and
                        x.is_lactose == dict(form.is_lactose.choices).get(form.is_lactose.data)][0]
        db.session.commit()
        return redirect(url_for('.get_sku'))
    form.name.data = sku.name
    form.size.data = sku.size
    form.percent = sku.boiling.percent
    form.is_lactose = sku.boiling.is_lactose
    return render_template('edit_sku.html', form=form)


@main.route('/delete_sku/<int:id>', methods=['DELETE'])
def delete_sku(id):
    sku = db.session.query(SKU).get_or_404(id)
    if sku:
        db.session.delete(sku)
        db.session.commit()
    return redirect(url_for('.get_sku'))




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
