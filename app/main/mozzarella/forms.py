from flask_restplus import ValidationError
from flask_wtf.file import FileRequired, FileField
from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    SelectField,
    IntegerField,
    FloatField,
    DateTimeField,
    TimeField,
)
from wtforms.validators import Required, Optional
from flask_wtf import FlaskForm

from ...models import (
    Packer,
    MozzarellaBoiling,
    MozzarellaLine,
    PackType,
    FormFactor,
    MozzarellaSKU,
    MozzarellaBoilingTechnology,
    Group,
    BatchNumber,
    MozzarellaFormFactor,
)
from ... import db
import datetime


class BoilingPlanFastForm(FlaskForm):
    validators = [FileRequired(message="Файл не выбран!")]
    input_file = FileField(
        label="Выберите файл",
        validators=validators,
    )
    date = DateTimeField(
        "Введите дату",
        format="%Y-%m-%d",
        default=datetime.datetime.today() + datetime.timedelta(days=1),
        validators=[Required()],
    )


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    batch_number = IntegerField(
        "Введите номер первой партии в текущем дне", validators=[Optional()]
    )
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])
    salt_beg_time = TimeField(
        'Начало первой подачи на линии "Пицца Чиз"',
        validators=[Optional()],
        default=datetime.time(7, 0),
    )
    water_beg_time = TimeField(
        'Начало первой подачи на линии "Моцарелла в воде"',
        validators=[Optional()],
        default=datetime.time(8, 0),
    )
    add_full_boiling = BooleanField(
        "Вставить полную мойку внутри дня по правилу 12 часов",
        validators=[Optional()],
        default=True,
    )


class SKUForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[Required()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    weight_netto = FloatField("Введите вес нетто", validators=[Optional()])
    packing_speed = IntegerField("Введите скорость фасовки", validators=[Optional()])
    shelf_life = IntegerField("Введите время хранения, д", validators=[Optional()])
    in_box = IntegerField(
        "Введите количество упаковок в коробке, шт", validators=[Optional()]
    )

    line = SelectField("Выберите линию", coerce=int, default=-1)
    packer = SelectField("Выберите тип фасовщика", coerce=int, default=-1)
    pack_type = SelectField("Выберите тип упаковки", coerce=int, default=-1)
    form_factor = SelectField("Выберите тип форм фактора", coerce=int, default=-1)
    boiling = SelectField("Выберите тип варки", coerce=int, default=-1)
    group = SelectField("Выберите название форм фактора", coerce=int, default=-1)

    submit = SubmitField(label="Сохранить")

    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)

        self.lines = db.session.query(MozzarellaLine).all()
        self.boilings = db.session.query(MozzarellaBoiling).all()
        self.packers = db.session.query(Packer).all()
        self.pack_types = db.session.query(PackType).all()
        self.form_factors = db.session.query(MozzarellaFormFactor).all()

        self.line.choices = list(enumerate(set([x.name for x in self.lines])))
        self.line.choices.append((-1, ""))

        self.packer.choices = list(enumerate(set([x.name for x in self.packers])))
        self.packer.choices.append((-1, ""))

        self.pack_type.choices = list(enumerate(set([x.name for x in self.pack_types])))
        self.pack_type.choices.append((-1, ""))

        self.form_factor.choices = list(
            enumerate(sorted(set([x.full_name for x in self.form_factors])))
        )
        self.form_factor.choices.append((-1, ""))

        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = (
            db.session.query(MozzarellaSKU)
            .filter_by(MozzarellaSKU.name == name.data)
            .first()
        )
        if sku is not None:
            raise ValidationError("SKU с таким именем уже существует")


class LineForm(FlaskForm):
    name = StringField("Введите название линии", validators=[Required()])
    pouring_time = IntegerField("Введите время налива", validators=[Required()])
    serving_time = IntegerField(
        "Введите время подачи и вымешивания", validators=[Required()]
    )
    chedderization_time = IntegerField(
        "Введите время чеддеризации", validators=[Required()]
    )
    melting_speed = IntegerField("Введите скорость плавления", validators=[Required()])


class BoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    pouring_time = IntegerField("Введите время налива", validators=[Optional()])
    soldification_time = IntegerField("Введите время схватки", validators=[Optional()])
    cutting_time = IntegerField(
        "Введите время резки и обсушки", validators=[Optional()]
    )
    pouring_off_time = IntegerField("Введите время слива", validators=[Optional()])
    extra_time = IntegerField(
        "Введите время на дополнительные затраты", validators=[Optional()]
    )
    line = SelectField("Выберите линию", coerce=int, default=-1)

    submit = SubmitField(label="Сохранить")

    def __init__(self, *args, **kwargs):
        super(BoilingTechnologyForm, self).__init__(*args, **kwargs)
        self.lines = db.session.query(MozzarellaLine).all()
        self.line.choices = list(enumerate(set([x.name for x in self.lines])))
        self.line.choices.append((-1, ""))


class FormFactorForm(FlaskForm):
    name = StringField("Название форм фактора", validators=[Optional()])
    line = StringField("Название линии", validators=[Optional()])
    first_cooling_time = IntegerField(
        "Введите время первого охлаждения", validators=[Optional()]
    )
    second_cooling_time = IntegerField(
        "Введите время второго охлаждения", validators=[Optional()]
    )
    salting_time = IntegerField("Введите время посолки", validators=[Optional()])


class WasherForm(FlaskForm):
    name = StringField("Название", validators=[Optional()])
    time = IntegerField("Введите время мойки", validators=[Optional()])


# class FormFactorForm(FlaskForm):
#     relative_weight = StringField('Введите вес форм фактора', validators=[Required()])
#     first_cooling_time = IntegerField('Введите первое время охлаждения', validators=[Optional()])
#     second_cooling_time = IntegerField('Введите второе время охлаждения', validators=[Optional()])
#     salting_time = IntegerField('Введите время посолки', validators=[Optional()])
#
#     def validate_form_factor(self, percent, ferment, is_lactose, line):
#         boiling = db.session.query(Boiling) \
#             .filter_by(Boiling.percent == percent.data) \
#             .filter_by(Boiling.is_lactose == is_lactose.data) \
#             .filter_by(Boiling.ferment == ferment.data) \
#             .filter_by(Boiling.line.name == line.data) \
#             .first()
#         if boiling is not None:
#             raise ValidationError('Варка с такими параметрами уже существует!')