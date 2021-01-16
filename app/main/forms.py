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
    batch_number = IntegerField('Введите номер последней партии', default=0, validators=[Optional()])
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









# class BoilingForm(FlaskForm):
#     percent = FloatField('Введите процент жирности', validators=[Optional()])
#     is_lactose = BooleanField('Укажите наличие лактозы', validators=[Optional()])
#     ferment = SelectField('Выберите тип закваски', coerce=int)
#     pouring_time = IntegerField('Введите время налива', validators=[Optional()])
#     soldification_time = IntegerField('Введите время схватки', validators=[Optional()])
#     cutting_time = IntegerField('Введите время резки и обсушки', validators=[Optional()])
#     pouring_off_time = IntegerField('Введите время слива', validators=[Optional()])
#     extra_time = IntegerField('Введите время на дополнительные затраты', validators=[Optional()])
#
#     serving_time = IntegerField('Введите время обслуживания', validators=[Optional()])
#     melting_time = IntegerField('Введите время плавления', validators=[Optional()])
#     speed = IntegerField('Введите скорость плавления', validators=[Optional()])
#
#     line = SelectField('Выберите линию', coerce=int, default=-1)
#     lines = None
#     submit = SubmitField('Выполнить расчет')
#
#     def __init__(self, *args, **kwargs):
#         super(BoilingForm, self).__init__(*args, **kwargs)
#         self.ferment.choices = list(enumerate(['Альче', 'Сакко']))
#         self.lines = db.session.query(Line).all()
#         self.line.choices = list(enumerate(set([x.name for x in self.lines])))
#         self.line.choices.append((-1, ''))
#
#
# class SKUForm(FlaskForm):
#     name = StringField('Введите имя SKU', validators=[Required()])
#     brand_name = StringField('Введите имя бренда', validators=[Optional()])
#     weight_netto = FloatField('Введите вес нетто', validators=[Optional()])
#     weight_form_factor = FloatField('Введите вес одного шарика', validators=[Optional()])
#     packing_speed = IntegerField('Введите скорость фасовки', validators=[Optional()])
#     output_per_ton = IntegerField('Введите выход с одной тонны, кг', validators=[Optional()])
#     shelf_life = IntegerField('Введите время хранения, д', validators=[Optional()])
#     packing_reconfiguration = IntegerField('Введите на перенастройки быстрой упаковки', validators=[Optional()])
#     packing_reconfiguration_format = IntegerField('Введите на перенастройки долгой упаковки', validators=[Optional()])
#
#     pack_type = SelectField('Выберите тип упаковки', coerce=int, default=-1)
#     percent = SelectField('Выберите процент жира', coerce=int)
#     packer = SelectField('Выберите тип фасовщика', coerce=int, default=-1)
#     ferment = SelectField('Выберите тип закваски', coerce=int)
#     is_lactose = SelectField('Выберите наличие лактозы', coerce=int)
#     form_factor = SelectField('Выберите форм фактор', coerce=int, default=-1)
#
#     bff = SelectField('Выберите форм фактор плавления', coerce=int, default=-1)
#
#     pack_types = None
#     packers = None
#     boilings = None
#     form_factors = None
#     bffs = None
#     submit = SubmitField('Submit')
#
#     def __init__(self, *args, **kwargs):
#         super(SKUForm, self).__init__(*args, **kwargs)
#         self.boilings = db.session.query(Boiling).all()
#         self.packers = db.session.query(Packer).all()
#         self.pack_types = db.session.query(PackType).all()
#         self.bffs = db.session.query(BoilingFormFactor).all()
#         self.form_factors = db.session.query(FormFactor).all()
#
#         self.ferment.choices = list(enumerate(set([x.ferment for x in self.boilings])))
#         self.percent.choices = list(enumerate(set([x.percent for x in self.boilings])))
#         self.is_lactose.choices = list(enumerate([True, False]))
#
#         self.packer.choices = list(enumerate(set([x.name for x in self.packers])))
#         self.packer.choices.append((-1, ''))
#
#         self.pack_type.choices = list(enumerate(set([x.name for x in self.pack_types])))
#         self.pack_type.choices.append((-1, ''))
#
#         self.form_factor.choices = list(enumerate(set([x.name for x in self.form_factors])))
#         self.form_factor.choices.append((-1, ''))
#
#         self.bff.choices = list(enumerate(set([x.weight for x in self.bffs])))
#         self.bff.choices.append((-1, ''))
#
#
# class PouringProcessForm(FlaskForm):
#     pouring_time = IntegerField('Pouring process time', validators=[Required()])
#     submit = SubmitField('Submit')
#
#
# class PouringProcess(FlaskForm):
#     pouring_time = IntegerField('Enter pouring time', validators=[Required()])
#     soldification_time = IntegerField('Enter soldification time', validators=[Required()])
#     cutting_time = IntegerField('Enter is lactose', validators=[Required()])
#
#
# class RequestForm(FlaskForm):
#     validators = [
#         FileRequired(message='There was no file!')
#     ]
#     input_file = FileField('', validators=validators)
#     date = DateTimeField('Введите дату', format="%Y-%m-%d", default=datetime.datetime.today, validators=[Required()])
#     submit = SubmitField(label="Отправить")
#
#
# class BoilingPlanForm(FlaskForm):
#     validators = [
#         FileRequired(message='Отсутствует файл!')
#     ]
#     batch_number = IntegerField('Введите номер последней партии', default=0, validators=[Optional()])
#     input_file = FileField('', validators=validators)
#     submit = SubmitField(label="Отправить")
#
#
# class ScheduleForm(FlaskForm):
#     validators = [
#         FileRequired(message='Отсутствует файл!')
#     ]
#     input_file = FileField('', validators=validators)
#     date = DateTimeField('Введите дату', format="%Y-%m-%d", default=datetime.datetime.today, validators=[Required()])
#     salt_beg_time = TimeField('Начало первой подачи на линии "Пицца Чиз"', validators=[Optional()], default=datetime.time(7, 0))
#     water_beg_time = TimeField('Начало первой подачи на линии "Моцарелла в воде"', validators=[Optional()], default=datetime.time(8, 0))
#     submit = SubmitField(label="Отправить")
#
#
# class StatisticForm(FlaskForm):
#     validators = [
#         FileRequired(message='Отсутствует файл!')
#     ]
#     input_file = FileField('', validators=validators)
#     submit = SubmitField(label="Отправить")
#
#
# class BoilingFormFactorForm(FlaskForm):
#     weight = IntegerField('Введите вес форм фактора плавления', validators=[Required()])
#     first_cooling_time = IntegerField('Введите время первого охлаждения (для Воды)', validators=[Optional()])
#     second_cooling_time = IntegerField('Введите время второго охлаждения (для Воды)', validators=[Optional()])
#     salting_time = IntegerField('Введите время посолки (для линии Соли)', validators=[Optional()])
#     submit = SubmitField(label='Сохранить')
#
#     def validate_weight(self, weight):
#         bffs = db.session.query(BoilingFormFactor).filter(BoilingFormFactor.weight == weight.data).first()
#         if bffs is not None:
#             raise ValidationError('Такой вес форм фактора уже существует!')

