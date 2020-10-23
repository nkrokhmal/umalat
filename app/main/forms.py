from flask_restplus import ValidationError
from flask_wtf.file import FileRequired, FileField
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField, FloatField, DateTimeField
from wtforms.validators import Required, Optional
from flask_wtf import FlaskForm
from ..models import Packing, Boiling
from .. import db
from datetime import datetime


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
    size = FloatField('Enter packing size', validators=[Optional()])
    percent = SelectField('Choose percent', coerce=int)
    packing = SelectField('Выберите тип фасовщика', coerce=int)
    is_lactose = SelectField('Choose is lactose', coerce=int)
    speed = IntegerField('Enter speed', validators=[Optional()])
    packing_reconfiguration = IntegerField('Введите на перенастройки быстрой упаковки', validators=[Optional()])
    packing_reconfiguration_format = IntegerField('Введите на перенастройки долгой упаковки', validators=[Optional()])

    packings = None
    boilings = None
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)
        self.boilings = db.session.query(Boiling).all()
        self.packings = db.session.query(Packing).all()

        self.packing.choices = list(enumerate(set([x.name for x in self.packings])))
        self.percent.choices = list(enumerate(set([x.percent for x in self.boilings])))
        self.is_lactose.choices = list(enumerate(set([x.is_lactose for x in self.boilings])))


class PouringProcessForm(FlaskForm):
    pouring_time = IntegerField('Pouring process time', validators=[Required()])
    submit = SubmitField('Submit')


class PouringProcess(FlaskForm):
    pouring_time = IntegerField('Enter pouring time', validators=[Required()])
    soldification_time = IntegerField('Enter soldification time', validators=[Required()])
    cutting_time = IntegerField('Enter is lactose', validators=[Required()])


class RequestForm(FlaskForm):
    validators = [
        FileRequired(message='There was no file!')
    ]

    input_file = FileField('', validators=validators)
    request_day = DateTimeField('Which date is your favorite?', format="%Y-%m-%d", default=datetime.today, validators=[Required()])
    submit = SubmitField(label="Submit")


