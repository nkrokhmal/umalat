from flask_restplus import ValidationError
from flask_wtf.file import FileRequired, FileField
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField, FloatField, DateTimeField
from wtforms.validators import Required, Optional
from flask_wtf import FlaskForm
from ..models import Packer, Boiling, Line, PackType
from .. import db
from datetime import datetime


class BoilingForm(FlaskForm):
    # Процессы самой варки
    percent = FloatField('Enter percentage', validators=[Optional()])
    priority = IntegerField('Enter priority', validators=[Optional()])
    is_lactose = BooleanField('Enter is lactose', validators=[Optional()])
    ferment = SelectField('Выберите фермент', coerce=int)
    pouring_time = IntegerField('Enter pouring time', validators=[Optional()])
    soldification_time = IntegerField('Enter soldification time', validators=[Optional()])
    cutting_time = IntegerField('Enter cutting time', validators=[Optional()])
    pouring_off_time = IntegerField('Enter pouring off time', validators=[Optional()])
    extra_time = IntegerField('Enter extra time', validators=[Optional()])
    # Процессы плавления
    serving_time = IntegerField('Enter serving time', validators=[Optional()])
    melting_time = IntegerField('Enter melting time', validators=[Optional()])
    speed = IntegerField('Enter speed', validators=[Optional()])
    first_cooling_time = IntegerField('Enter first cooling time', validators=[Optional()])
    second_cooling_time = IntegerField('Enter seconds cooling time', validators=[Optional()])
    salting_time = IntegerField('Enter salting time', validators=[Optional()])
    # сабмит
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(BoilingForm, self).__init__(*args, **kwargs)
        self.ferment.choices = list(enumerate(['Альче', 'Сакко']))


class SKUForm(FlaskForm):
    name = StringField('Введите имя SKU', validators=[Required()])
    brand_name = StringField('Введите имя бренда', validators=[Optional()])
    weight_netto = FloatField('Введите вес нетто', validators=[Optional()])
    weight_form_factor = FloatField('Введите вес одного шарика', validators=[Optional()])
    packing_speed = IntegerField('Введите скорость фасовки', validators=[Optional()])
    output_per_ton = IntegerField('Введите выход с одной тонны, кг', validators=[Optional()])
    shelf_life = IntegerField('Введите время хранения, д', validators=[Optional()])
    packing_reconfiguration = IntegerField('Введите на перенастройки быстрой упаковки', validators=[Optional()])
    packing_reconfiguration_format = IntegerField('Введите на перенастройки долгой упаковки', validators=[Optional()])

    pack_type = SelectField('Выберите тип упаковки', coerce=int, default=-1)
    percent = SelectField('Выберите процент жира', coerce=int)
    packer = SelectField('Выберите тип фасовщика', coerce=int, default=-1)
    ferment = SelectField('Выберите тип закваски', coerce=int)
    line = SelectField('Выберите линию', coerce=int, default=-1)
    is_lactose = SelectField('Выберите наличие лактозы', coerce=int)

    pack_types = None
    lines = None
    packers = None
    boilings = None
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)
        self.boilings = db.session.query(Boiling).all()
        self.packers = db.session.query(Packer).all()
        self.lines = db.session.query(Line).all()
        self.pack_types = db.session.query(PackType).all()

        self.ferment.choices = list(enumerate(set([x.ferment for x in self.boilings])))
        self.percent.choices = list(enumerate(set([x.percent for x in self.boilings])))
        self.is_lactose.choices = list(enumerate(set([x.is_lactose for x in self.boilings])))
        self.line.choices = list(enumerate(set([x.name for x in self.lines])))
        self.line.choices.append((-1, ''))
        self.packer.choices = list(enumerate(set([x.name for x in self.packers])))
        self.packer.choices.append((-1, ''))
        self.pack_type.choices = list(enumerate(set([x.name for x in self.pack_types])))
        self.pack_type.choices.append((-1, ''))


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


