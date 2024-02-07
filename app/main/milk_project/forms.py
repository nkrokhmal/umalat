from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import *
from wtforms.validators import DataRequired, Optional

from app.imports.runtime import *
from app.models import *


class UploadForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])
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
        validators=[DataRequired()],
    )


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])
    beg_time = StringField(
        "Время начала подготовки цеха к работе",
        validators=[Optional()],
        default="07:00",
    )
    packing_beg_time = StringField(
        "Время начала паковки",
        validators=[Optional()],
        default="11:00",
    )


class BrynzaScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])
    beg_time = StringField(
        "Начало первой варки",
        validators=[Optional()],
        default="07:00",
    )


class MilkProjectBoilingForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    output_coeff = FloatField("Коэффициент", validators=[Optional()])
    output_kg = IntegerField("Выход", validators=[Optional()])


class MilkProjectBoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    mixture_collecting_time = IntegerField("", validators=[Optional()])
    processing_time = IntegerField("", validators=[Optional()])
    red_time = IntegerField("", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class SKUMilkProjectForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[DataRequired()])
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
        super(SKUMilkProjectForm, self).__init__(*args, **kwargs)

        self.boilings = db.session.query(MilkProjectBoiling).all()
        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(MilkProjectSKU).filter_by(MilkProjectSKU.name == name.data).first()
        if sku is not None:
            raise flask_restplus.ValidationError("SKU с таким именем уже существует")


class CopySKUForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[DataRequired()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    code = StringField("Введите код SKU", validators=[Optional()])
