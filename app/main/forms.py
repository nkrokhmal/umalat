from flask_restplus import ValidationError
from flask_wtf.file import FileRequired, FileField
from wtforms import fields, StringField, SubmitField, BooleanField, SelectField, IntegerField, FloatField, DateTimeField, SelectMultipleField
from wtforms.validators import Required, Optional
from flask_wtf import FlaskForm
from ..models import Packer, Boiling, Line, PackType, FormFactor, BoilingFormFactor
from .. import db
from datetime import datetime


class BoilingForm(FlaskForm):
    percent = FloatField('Введите процент жирности', validators=[Optional()])
    is_lactose = BooleanField('Укажите наличие лактозы', validators=[Optional()])
    ferment = SelectField('Выберите тип закваски', coerce=int)
    pouring_time = IntegerField('Введите время налива', validators=[Optional()])
    soldification_time = IntegerField('Введите время схватки', validators=[Optional()])
    cutting_time = IntegerField('Введите время резки и обсушки', validators=[Optional()])
    pouring_off_time = IntegerField('Введите время слива', validators=[Optional()])
    extra_time = IntegerField('Введите время на дополнительные затраты', validators=[Optional()])

    serving_time = IntegerField('Введите время обслуживания', validators=[Optional()])
    melting_time = IntegerField('Введите время плавления', validators=[Optional()])
    speed = IntegerField('Введите скорость плавления', validators=[Optional()])
    first_cooling_time = IntegerField('Введите первое время охлаждения', validators=[Optional()])
    second_cooling_time = IntegerField('Введите второе время охлаждения', validators=[Optional()])
    salting_time = IntegerField('Введите время посолки', validators=[Optional()])

    line = SelectField('Выберите линию', coerce=int, default=-1)
    lines = None
    submit = SubmitField('Выполнить расчет')

    def __init__(self, *args, **kwargs):
        super(BoilingForm, self).__init__(*args, **kwargs)
        self.ferment.choices = list(enumerate(['Альче', 'Сакко']))
        self.lines = db.session.query(Line).all()
        self.line.choices = list(enumerate(set([x.name for x in self.lines])))
        self.line.choices.append((-1, ''))


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
    is_lactose = SelectField('Выберите наличие лактозы', coerce=int)
    form_factor = SelectField('Выберите форм фактор', coerce=int, default=-1)

    bff = SelectField('Выберите форм фактор плавления', coerce=int, default=-1)

    pack_types = None
    packers = None
    boilings = None
    form_factors = None
    bffs = None
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)
        self.boilings = db.session.query(Boiling).all()
        self.packers = db.session.query(Packer).all()
        self.pack_types = db.session.query(PackType).all()
        self.bffs = db.session.query(BoilingFormFactor).all()
        self.form_factors = db.session.query(FormFactor).all()

        self.ferment.choices = list(enumerate(set([x.ferment for x in self.boilings])))
        self.percent.choices = list(enumerate(set([x.percent for x in self.boilings])))
        self.is_lactose.choices = list(enumerate([True, False]))

        self.packer.choices = list(enumerate(set([x.name for x in self.packers])))
        self.packer.choices.append((-1, ''))

        self.pack_type.choices = list(enumerate(set([x.name for x in self.pack_types])))
        self.pack_type.choices.append((-1, ''))

        self.form_factor.choices = list(enumerate(set([x.name for x in self.form_factors])))
        self.form_factor.choices.append((-1, ''))

        self.bff.choices = list(enumerate(set([x.weight for x in self.bffs])))
        self.bff.choices.append((-1, ''))


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
    date = DateTimeField('Введите дату', format="%Y-%m-%d", default=datetime.today, validators=[Required()])
    submit = SubmitField(label="Submit")


class ScheduleForm(FlaskForm):
    validators = [
        FileRequired(message='Отсутствует файл!')
    ]
    input_file = FileField('', validators=validators)
    date = DateTimeField('Введите дату', format="%Y-%m-%d", default=datetime.today, validators=[Required()])
    submit = SubmitField(label="Submit")


class StatisticForm(FlaskForm):
    validators = [
        FileRequired(message='Отсутствует файл!')
    ]
    input_file = FileField('', validators=validators)
    submit = SubmitField(label="Отправить")

