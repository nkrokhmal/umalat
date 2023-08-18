from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import *
from wtforms.validators import Optional, Required

from app.imports.runtime import *
from app.models import *


class BoilingPlanForm(FlaskForm):
    validators = [FileRequired(message="Файл не выбран!")]
    input_file = FileField(
        label="Выберите файл",
        validators=validators,
    )
    add_auto_boilings = BooleanField(
        "Вставить дополнительные SKU",
        validators=[Optional()],
        default=False,
    )
    date = DateTimeField(
        "Введите дату",
        format="%Y-%m-%d",
        default=datetime.today() + timedelta(days=1),
        validators=[Required()],
    )


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])
    beg_time = TimeField(
        "Время начала подготовки цеха к работе",
        validators=[Optional()],
        default=time(8, 0),
    )


class AdygeaBoilingForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    output_coeff = FloatField("Коэффициент", validators=[Optional()])
    input_kg = IntegerField("Вход", validators=[Optional()])
    output_kg = IntegerField("Выход", validators=[Optional()])


class AdygeaBoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    collecting_time = IntegerField("", validators=[Optional()])
    coagulation_time = IntegerField("", validators=[Optional()])
    pouring_off_time = IntegerField("", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class SKUAdygeaForm(FlaskForm):
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
        super(SKUAdygeaForm, self).__init__(*args, **kwargs)

        self.boilings = db.session.query(AdygeaBoiling).all()
        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(AdygeaSKU).filter_by(AdygeaSKU.name == name.data).first()
        if sku is not None:
            raise flask_restplus.ValidationError("SKU с таким именем уже существует")


class CopySKUForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[Required()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    code = StringField("Введите код SKU", validators=[Optional()])
