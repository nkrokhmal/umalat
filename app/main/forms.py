from flask_restplus import ValidationError
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField, FloatField
from wtforms.validators import Required
from flask_wtf import FlaskForm
from ..models import MeltingProcess, Boiling
from .. import db


class BoilingForm(FlaskForm):
    # Процессы самой варки
    percent = FloatField('Enter percentage', validators=[Required()])
    priority = IntegerField('Enter priority', validators=[Required()])
    is_lactose = BooleanField('Enter is lactose')
    # Процессы налива
    pouring_time = IntegerField('Enter pouring time', validators=[Required()])
    soldification_time = IntegerField('Enter soldification time', validators=[Required()])
    cutting_time = IntegerField('Enter cutting time', validators=[Required()])
    pouring_off_time = IntegerField('Enter pouring off time', validators=[Required()])
    extra_time = IntegerField('Enter extra time', [Required()])
    # Процессы плавления
    serving_time = IntegerField('Enter serving time', [Required()])
    melting_time = IntegerField('Enter melting time', [Required()])
    speed = IntegerField('Enter speed', [Required()])
    first_cooling_time = IntegerField('Enter first cooling time', [Required()])
    second_cooling_time = IntegerField('Enter seconds cooling time', [Required()])
    salting_time = IntegerField('Enter salting time', [Required()])
    # сабмит
    submit = SubmitField('Submit')


class SKUForm(FlaskForm):
    name = StringField('Enter SKU name', validators=[Required()])
    size = FloatField('Enter packing size', validators=[Required()])
    percent = SelectField('Choose percent', coerce=int)
    is_lactose = SelectField('Choose is lactose', coerce=int)
    speed = IntegerField('Enter speed', validators=[Required()])
    packing_reconfiguration = IntegerField('Введите на перенастройки упаковки', validators=[Required()])
    boilings = None
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)
        self.boilings = db.session.query(Boiling).all()
        self.percent.choices = list(enumerate(set([x.percent for x in self.boilings])))
        self.is_lactose.choices = list(enumerate(set([x.is_lactose for x in self.boilings])))


class PouringProcessForm(FlaskForm):
    pouring_time = IntegerField('Pouring process time', validators=[Required()])
    submit = SubmitField('Submit')


class PouringProcess(FlaskForm):
    pouring_time = IntegerField('Enter pouring time', validators=[Required()])
    soldification_time = IntegerField('Enter soldification time', validators=[Required()])
    cutting_time = IntegerField('Enter is lactose', validators=[Required()])



class CheeseForm(FlaskForm):
    cheese_name = StringField('Cheese name', validators=[Required()])
    leaven_time = IntegerField('Leaven time in minutes', validators=[Required()])
    solidification_time = IntegerField('Solidification time in minutes', validators=[Required()])
    cutting_time = IntegerField('Cutting time in minutes', validators=[Required()])
    draining_time = IntegerField('Draining time in minutes', validators=[Required()])
    cheese_maker = SelectField('Cheese maker', coerce=int)
    submit = SubmitField('Submit')

    # def __init__(self, *args, **kwargs):
    #     super(CheeseForm, self).__init__(*args, **kwargs)
    #     self.cheese_maker.choices = [(cm.id, cm.cheese_maker_name) for cm in
    #                                  db.session.query(CheeseMaker).order_by(CheeseMaker.cheese_maker_name).all()]


class CheeseMakerForm(FlaskForm):
    cheese_maker_name = StringField('Name of cheese maker', validators=[Required()])
    submit = SubmitField('Submit')
