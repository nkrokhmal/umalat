from app.imports.runtime import *

from app.models import *


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
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    weight_netto = FloatField("Введите вес нетто", validators=[Optional()])
    packing_speed = IntegerField("Введите скорость фасовки", validators=[Optional()])
    shelf_life = IntegerField("Введите время хранения, д", validators=[Optional()])
    in_box = IntegerField(
        "Введите количество упаковок в коробке, шт", validators=[Optional()]
    )

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
        sku = (
            db.session.query(CreamCheeseSKU)
            .filter_by(CreamCheeseSKU.name == name.data)
            .first()
        )
        if sku is not None:
            raise ValidationError("SKU с таким именем уже существует")


class SKUMascarponeForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[Required()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    weight_netto = FloatField("Введите вес нетто", validators=[Optional()])
    packing_speed = IntegerField("Введите скорость фасовки", validators=[Optional()])
    shelf_life = IntegerField("Введите время хранения, д", validators=[Optional()])
    in_box = IntegerField(
        "Введите количество упаковок в коробке, шт", validators=[Optional()]
    )

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
        sku = (
            db.session.query(MascarponeSKU)
            .filter_by(MascarponeSKU.name == name.data)
            .first()
        )
        if sku is not None:
            raise ValidationError("SKU с таким именем уже существует")


class MascarponeBoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    pouring_time = IntegerField("Введите время налива", validators=[Optional()])
    heating_time = IntegerField("Введите время нагрева", validators=[Optional()])
    adding_lactic_acid_time = IntegerField(
        "Введите время добавления лактозы", validators=[Optional()]
    )
    separation_time = IntegerField("Введите время сепарации", validators=[Optional()])
    fermentator_name = SelectField("Выберите ферментатор", coerce=int, default=-1)
    submit = SubmitField(label="Сохранить")

    def __init__(self, *args, **kwargs):
        super(MascarponeBoilingTechnologyForm, self).__init__(*args, **kwargs)

        self.fermentators = db.session.query(MascarponeSourdough).all()
        self.fermentator_name.choices = list(
            enumerate(set([x.to_str() for x in self.fermentators]))
        )


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    batch_number = IntegerField(
        "Введите номер первой партии в текущем дне", validators=[Optional()]
    )
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])
    beg_time = TimeField(
        'Начало первой подачи"',
        validators=[Optional()],
        default=time(7, 0),
    )
