from flask_restplus import ValidationError
from flask_wtf.file import FileRequired, FileField
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField, FloatField, DateTimeField, TimeField
from wtforms.validators import Required, Optional
from flask_wtf import FlaskForm
from ..models_new import Packer, Boiling, Line, PackType, FormFactor, SKU, BoilingTechnology, Group
from .. import db
import datetime


class SkuPlanForm(FlaskForm):
    validators = [
        FileRequired(message='There was no file!')
    ]
    input_file = FileField('', validators=validators)
    date = DateTimeField('Введите дату', format="%Y-%m-%d", default=datetime.datetime.today, validators=[Required()])
    submit = SubmitField(label='Отправить')


class BoilingPlanForm(FlaskForm):
    validators = [
        FileRequired(message='Отсутствует файл!')
    ]
    batch_number = IntegerField('Введите номер первой партии в текущем дне', default=1, validators=[Optional()])
    input_file = FileField('', validators=validators)
    submit = SubmitField(label="Отправить")


class FileForm(FlaskForm):
    validators = [
        FileRequired(message='Отсутствует файл!')
    ]
    input_file = FileField('', validators=validators)
    submit = SubmitField(label="Отправить")


class ScheduleForm(FlaskForm):
    validators = [
        FileRequired(message='Отсутствует файл!')
    ]
    input_file = FileField('', validators=validators)
    date = DateTimeField('Введите дату', format="%Y-%m-%d", default=datetime.datetime.today, validators=[Required()])
    salt_beg_time = TimeField('Начало первой подачи на линии "Пицца Чиз"', validators=[Optional()], default=datetime.time(7, 0))
    water_beg_time = TimeField('Начало первой подачи на линии "Моцарелла в воде"', validators=[Optional()], default=datetime.time(8, 0))
    submit = SubmitField(label='Отправить')


class SKUForm(FlaskForm):
    name = StringField('Введите имя SKU', validators=[Required()])
    brand_name = StringField('Введите имя бренда', validators=[Optional()])
    weight_netto = FloatField('Введите вес нетто', validators=[Optional()])
    packing_speed = IntegerField('Введите скорость фасовки', validators=[Optional()])
    shelf_life = IntegerField('Введите время хранения, д', validators=[Optional()])

    line = SelectField('Выберите линию', coerce=int, default=-1)
    packer = SelectField('Выберите тип фасовщика', coerce=int, default=-1)
    pack_type = SelectField('Выберите тип упаковки', coerce=int, default=-1)
    form_factor = SelectField('Выберите тип форм фактора', coerce=int, default=-1)
    boiling = SelectField('Выберите тип варки', coerce=int, default=-1)

    submit = SubmitField(label='Сохранить')

    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)

        self.lines = db.session.query(Line).all()
        self.boilings = db.session.query(Boiling).all()
        self.packers = db.session.query(Packer).all()
        self.pack_types = db.session.query(PackType).all()
        self.form_factors = db.session.query(FormFactor).all()

        self.line.choices = list(enumerate(set([x.name for x in self.lines])))
        self.line.choices.append((-1, ''))

        self.packer.choices = list(enumerate(set([x.name for x in self.packers])))
        self.packer.choices.append((-1, ''))

        self.pack_type.choices = list(enumerate(set([x.name for x in self.pack_types])))
        self.pack_type.choices.append((-1, ''))

        self.form_factor.choices = list(enumerate(sorted(set([x.full_name for x in self.form_factors]))))
        self.form_factor.choices.append((-1, ''))

        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ''))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(SKU).filter_by(SKU.name == name.data).first()
        if sku is not None:
            raise ValidationError('SKU с таким именем уже существует')


class BoilingForm(FlaskForm):
    percent = FloatField('Введите процент жирности', validators=[Optional()])
    is_lactose = BooleanField('Укажите наличие лактозы', validators=[Optional()])
    ferment = SelectField('Выберите тип закваски', coerce=int, default=-1)
    pouring_time = IntegerField('Введите время налива', validators=[Optional()])
    soldification_time = IntegerField('Введите время схватки', validators=[Optional()])
    cutting_time = IntegerField('Введите время резки и обсушки', validators=[Optional()])
    pouring_off_time = IntegerField('Введите время слива', validators=[Optional()])
    extra_time = IntegerField('Введите время на дополнительные затраты', validators=[Optional()])

    line = SelectField('Выберите линию', coerce=int, default=-1)

    submit = SubmitField(label='Сохранить')

    def __init__(self, *args, **kwargs):
        super(BoilingForm, self).__init__(*args, **kwargs)
        self.boiling_technologies = db.session.query(BoilingTechnology).all()
        self.ferment.choices = list(enumerate(['Альче', 'Сакко']))
        self.ferment.choices.append((-1, ''))

        self.lines = db.session.query(Line).all()
        self.line.choices = list(enumerate(set([x.name for x in self.lines])))
        self.line.choices.append((-1, ''))

    def validate_boiling(self, percent, ferment, is_lactose, line):
        boiling = db.session.query(Boiling)\
            .filter_by(Boiling.percent == percent.data)\
            .filter_by(Boiling.is_lactose == is_lactose.data)\
            .filter_by(Boiling.ferment == ferment.data)\
            .filter_by(Boiling.line.name == line.data)\
            .first()
        if boiling is not None:
            raise ValidationError('Варка с такими параметрами уже существует!')


class FormFactorForm(FlaskForm):
    relative_weight = StringField('Введите вес форм фактора', validators=[Required()])
    group = SelectField('Выберите название форм фактора', coerce=int, default=-1)
    first_cooling_time = IntegerField('Введите первое время охлаждения', validators=[Optional()])
    seconds_cooling_time = IntegerField('Введите второе время охлаждения', validators=[Optional()])
    salting_time = IntegerField('Введите время посолки', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(FormFactorForm, self).__init__(*args, **kwargs)
        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ''))

    def validate_form_factor(self, percent, ferment, is_lactose, line):
        boiling = db.session.query(Boiling) \
            .filter_by(Boiling.percent == percent.data) \
            .filter_by(Boiling.is_lactose == is_lactose.data) \
            .filter_by(Boiling.ferment == ferment.data) \
            .filter_by(Boiling.line.name == line.data) \
            .first()
        if boiling is not None:
            raise ValidationError('Варка с такими параметрами уже существует!')
