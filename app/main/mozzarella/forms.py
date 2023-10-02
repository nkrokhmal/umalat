from app.imports.runtime import *  # isort: skip
import wtforms

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms.validators import DataRequired, Optional

from app.main.validators import *
from app.models import *


class BoilingPlanFastForm(FlaskForm):
    input_file = wtforms.FileField(
        label="Выберите файл",
        validators=[FileRequired(message="Файл не выбран!")],
    )
    file_not_calculated = wtforms.FileField(
        label="Выберите файл не посчитанного на складе",
        validators=[Optional()],
    )
    date = wtforms.DateTimeField(
        "Введите дату",
        format="%Y-%m-%d",
        default=datetime.today() + timedelta(days=1),
        validators=[DataRequired()],
    )


class UploadForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    date = wtforms.DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])
    input_file = wtforms.FileField("", validators=validators)


class ScheduleForm(FlaskForm):
    input_file = wtforms.FileField("", validators=[FileRequired(message="Отсутствует файл!")])
    batch_number = wtforms.IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    date = wtforms.DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])
    salt_beg_time = wtforms.StringField(
        'Начало первой подачи на линии "Пицца Чиз"',
        validators=[Optional()],
        default="07:00",
    )
    water_beg_time = wtforms.StringField(
        'Начало первой подачи на линии "Моцарелла в воде"',
        validators=[Optional()],
        default="08:00",
    )
    exact_melting_time_by_line = wtforms.SelectField(
        "Выберите линию, по которой время будет выставляться точно (по оставшейся - приблизительно)",
        validators=[Optional()],
        choices=[(LineName.SALT, LineName.SALT), (LineName.WATER, LineName.WATER)],
        default=LineName.SALT,
    )
    optimize = wtforms.BooleanField(
        "Оптимизировать время оставшейся линии",
        validators=[Optional()],
        default=True,
    )
    add_full_boiling = wtforms.BooleanField(
        "Вставить короткую мойку внутри дня по правилу 15 часов",
        validators=[Optional()],
        default=True,
    )


class CopySKUForm(FlaskForm):
    name = wtforms.StringField("Введите имя SKU", validators=[DataRequired()])
    brand_name = wtforms.StringField("Введите имя бренда", validators=[Optional()])
    code = wtforms.StringField("Введите код SKU", validators=[Optional()])


class SKUForm(FlaskForm):
    name = wtforms.StringField("Введите имя SKU", validators=[DataRequired()])
    brand_name = wtforms.StringField("Введите имя бренда", validators=[Optional()])
    weight_netto = wtforms.FloatField("Введите вес нетто", validators=[Optional()])
    packing_speed = wtforms.IntegerField("Введите скорость фасовки", validators=[Optional()])
    melting_speed = wtforms.IntegerField("Введите скорость плавления", validators=[Optional()])
    shelf_life = wtforms.IntegerField("Введите время хранения, д", validators=[Optional()])
    code = wtforms.StringField("Введите код SKU", validators=[Optional()])
    in_box = wtforms.IntegerField("Введите количество упаковок в коробке, шт", validators=[Optional()])

    line = wtforms.SelectField("Выберите линию", coerce=int, default=-1)
    packer = wtforms.SelectField("Выберите тип фасовщика", coerce=int, default=-1)
    pack_type = wtforms.SelectField("Выберите тип упаковки", coerce=int, default=-1)
    form_factor = wtforms.SelectField("Выберите тип форм фактора", coerce=int, default=-1)
    boiling = wtforms.SelectField("Выберите тип варки", coerce=int, default=-1)
    group = wtforms.SelectField("Выберите название форм фактора", coerce=int, default=-1)

    submit = wtforms.SubmitField(label="Сохранить")

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

        self.form_factor.choices = list(enumerate(sorted(set([x.full_name for x in self.form_factors]))))
        self.form_factor.choices.append((-1, ""))

        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(MozzarellaSKU).filter_by(MozzarellaSKU.name == name.data).first()
        if sku is not None:
            # todo: fix
            ...
            # raise flask_restplus.ValidationError("SKU с таким именем уже существует")


class LineForm(FlaskForm):
    name = wtforms.StringField("Введите название линии", validators=[DataRequired()])
    pouring_time = wtforms.IntegerField("Введите время налива", validators=[DataRequired()])
    serving_time = wtforms.IntegerField("Введите время подачи и вымешивания", validators=[DataRequired()])
    chedderization_time = wtforms.IntegerField("Введите время чеддеризации", validators=[DataRequired()])
    output_kg = wtforms.IntegerField("Выход", validators=[DataRequired()])


class BoilingTechnologyForm(FlaskForm):
    name = wtforms.StringField("Название варки", validators=[Optional()])
    pouring_time = wtforms.IntegerField("Введите время налива", validators=[Optional()])
    soldification_time = wtforms.IntegerField("Введите время схватки", validators=[Optional()])
    cutting_time = wtforms.IntegerField("Введите время резки и обсушки", validators=[Optional()])
    pouring_off_time = wtforms.IntegerField("Введите время слива", validators=[Optional()])
    extra_time = wtforms.IntegerField("Введите время на дополнительные затраты", validators=[Optional()])
    line = wtforms.SelectField("Выберите линию", coerce=int, default=-1)

    submit = wtforms.SubmitField(label="Сохранить")

    def __init__(self, *args, **kwargs):
        super(BoilingTechnologyForm, self).__init__(*args, **kwargs)
        self.lines = db.session.query(MozzarellaLine).all()
        self.line.choices = list(enumerate(set([x.name for x in self.lines])))
        self.line.choices.append((-1, ""))


class FormFactorForm(FlaskForm):
    name = wtforms.StringField("Название форм фактора", validators=[Optional()])
    line = wtforms.StringField("Название линии", validators=[Optional()])
    first_cooling_time = wtforms.IntegerField("Введите время первого охлаждения", validators=[Optional()])
    second_cooling_time = wtforms.IntegerField("Введите время второго охлаждения", validators=[Optional()])
    salting_time = wtforms.IntegerField("Введите время посолки", validators=[Optional()])


class WasherForm(FlaskForm):
    name = wtforms.StringField("Название", validators=[Optional()])
    time = wtforms.IntegerField("Введите время мойки", validators=[Optional()])


class ApproveForm(FlaskForm):
    file_name = wtforms.StringField("Filename", validators=[Optional()])
    date = wtforms.StringField("Date", validators=[Optional()])
    submit = wtforms.SubmitField(label="Подтвердить")
