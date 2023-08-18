from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import *
from wtforms.validators import Optional, Required

from app.imports.runtime import *
from app.models import *


class UploadForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])
    input_file = FileField("", validators=validators)


class BoilingPlanForm(FlaskForm):
    validators = [FileRequired(message="Файл не выбран!")]
    input_file = FileField(
        label="Выберите файл",
        validators=validators,
    )
    date = DateTimeField(
        "Введите дату",
        format="%Y-%m-%d",
        default=datetime.today() + timedelta(days=1),
        validators=[Required()],
    )


class SKUCreamCheeseForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[Required()])
    code = StringField("Введите код SKU", validators=[Optional()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    weight_netto = FloatField("Введите вес нетто", validators=[Optional()])
    packing_speed = IntegerField("Введите скорость фасовки", validators=[Optional()])
    shelf_life = IntegerField("Введите время хранения, д", validators=[Optional()])
    in_box = IntegerField("Введите количество упаковок в коробке, шт", validators=[Optional()])

    boiling = SelectField("Выберите тип варки", coerce=int, default=-1)
    group = SelectField("Выберите название форм фактора", coerce=int, default=-1)

    submit = SubmitField(label="Сохранить")

    def __init__(self, *args, **kwargs):
        super(SKUCreamCheeseForm, self).__init__(*args, **kwargs)

        self.boilings = db.session.query(CreamCheeseBoiling).all()
        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(CreamCheeseSKU).filter_by(CreamCheeseSKU.name == name.data).first()
        if sku is not None:
            raise flask_restplus.ValidationError("SKU с таким именем уже существует")


class CopySKUForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[Required()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    code = StringField("Введите код SKU", validators=[Optional()])


class SKUMascarponeForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[Required()])
    code = StringField("Введите код SKU", validators=[Optional()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    weight_netto = FloatField("Введите вес нетто", validators=[Optional()])
    packing_speed = IntegerField("Введите скорость фасовки", validators=[Optional()])
    shelf_life = IntegerField("Введите время хранения, д", validators=[Optional()])
    in_box = IntegerField("Введите количество упаковок в коробке, шт", validators=[Optional()])

    boiling = SelectField("Выберите тип варки", coerce=int, default=-1)
    group = SelectField("Выберите название форм фактора", coerce=int, default=-1)

    submit = SubmitField(label="Сохранить")

    def __init__(self, *args, **kwargs):
        super(SKUMascarponeForm, self).__init__(*args, **kwargs)

        self.boilings = db.session.query(MascarponeBoiling).all()
        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(MascarponeSKU).filter_by(MascarponeSKU.name == name.data).first()
        if sku is not None:
            raise flask_restplus.ValidationError("SKU с таким именем уже существует")


class MascarponeBoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    pouring_time = IntegerField("Введите время налива", validators=[Optional()])
    heating_time = IntegerField("Введите время нагрева", validators=[Optional()])
    adding_lactic_acid_time = IntegerField("Введите время добавления лактозы", validators=[Optional()])
    pumping_off_time = IntegerField("Введите время слива", validators=[Optional()])
    ingredient_time = IntegerField("Введите время внесения ингредиентов", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class CreamCheeseBoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    cooling_time = IntegerField("Введите время охлаждения", validators=[Optional()])
    separation_time = IntegerField("Введите время сепарирования", validators=[Optional()])
    salting_time = IntegerField("Введите время посолки", validators=[Optional()])
    p_time = IntegerField("Введите время П", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)

    mascarpone_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    cream_cheese_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    robiola_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    cottage_cheese_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    cream_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])

    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])
    beg_time = StringField(
        'Начало первой подачи"',
        validators=[Optional()],
        default="06:00",
    )
