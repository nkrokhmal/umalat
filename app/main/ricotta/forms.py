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


class CopySKUForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[Required()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    code = StringField("Введите код SKU", validators=[Optional()])


class SKUForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[Required()])
    code = StringField("Введите код SKU", validators=[Optional()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    weight_netto = FloatField("Введите вес нетто", validators=[Optional()])
    packing_speed = FloatField("Введите скорость фасовки", validators=[Optional()])
    shelf_life = IntegerField("Введите время хранения, д", validators=[Optional()])
    in_box = IntegerField("Введите количество упаковок в коробке, шт", validators=[Optional()])
    output_per_tank = FloatField("Выход на танк, шт", validators=[Optional()])

    boiling = SelectField("Выберите тип варки", coerce=int, default=-1)
    group = SelectField("Выберите название форм фактора", coerce=int, default=-1)

    submit = SubmitField(label="Сохранить")

    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)

        self.boilings = db.session.query(RicottaBoiling).all()
        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(RicottaSKU).filter_by(RicottaSKU.name == name.data).first()
        if sku is not None:
            raise flask_restplus.ValidationError("SKU с таким именем уже существует")


class LineForm(FlaskForm):
    name = StringField("Введите название линии", validators=[Required()])
    input_ton = IntegerField("Введите количество литров в одном танке", validators=[Required()])


class BoilingForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    flavoring_agent = StringField("Добавка", validators=[Optional()])
    percent = IntegerField("Процент", validators=[Optional()])
    number_of_tanks = IntegerField("Число танков", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class BoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    heating_time = IntegerField("Введите время нагрева", validators=[Optional()])
    delay_time = IntegerField("Введите время выдержки", validators=[Optional()])
    protein_harvest_time = IntegerField("Введите время сбора белка", validators=[Optional()])
    abandon_time = IntegerField("Введите время заброса в бак", validators=[Optional()])
    pumping_out_time = IntegerField("Введите время слива сыворотки", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class AnalysisForm(FlaskForm):
    preparation_time = IntegerField("Введите время нагрева", validators=[Optional()])
    analysis_time = IntegerField("Введите время выдержки", validators=[Optional()])
    pumping_time = IntegerField("Введите время сбора белка", validators=[Optional()])
    boiling_name = StringField("Выберите варку", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])
    beg_time = StringField(
        'Начало первой подачи"',
        validators=[Optional()],
        default="07:00",
    )
