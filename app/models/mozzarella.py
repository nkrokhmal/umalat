import numpy as np
from ..enum import LineName
from . import db, SKU, Line, FormFactor, Boiling, BoilingTechnology, backref


class MozzarellaSKU(SKU):
    __tablename__ = "mozzarella_skus"
    __mapper_args__ = {"polymorphic_identity": "mozzarella_skus"}

    id = db.Column(db.Integer, db.ForeignKey("skus.id"), primary_key=True)
    production_by_request = db.Column(db.Boolean)
    packing_by_request = db.Column(db.Boolean)

    @property
    def colour(self):
        COLOURS = {
            "Для пиццы": "#E5B7B6",
            "Моцарелла": "#DAE5F1",
            "Фиор Ди Латте": "#CBC0D9",
            "Чильеджина": "#E5DFEC",
            "Качокавалло": "#F1DADA",
            "Сулугуни": "#F1DADA",
            "Терка": "#FFEBE0",
        }
        if "Терка" not in self.form_factor.name:
            return COLOURS[self.group.name]
        else:
            return COLOURS["Терка"]


class MozzarellaLine(Line):
    __tablename__ = "mozzarella_lines"
    __mapper_args__ = {"polymorphic_identity": "mozzarella_lines"}

    id = db.Column(db.Integer, db.ForeignKey("lines.id"), primary_key=True)
    pouring_time = db.Column(db.Integer)
    serving_time = db.Column(db.Integer)
    melting_speed = db.Column(db.Integer)
    chedderization_time = db.Column(db.Integer)

    @property
    def name_short(self):
        if self.name == LineName.SALT:
            return "Соль"
        elif self.name == LineName.WATER:
            return "Вода"
        else:
            return None


class MozzarellaFormFactor(FormFactor):
    __tablename__ = "mozzarella_form_factors"
    __mapper_args__ = {"polymorphic_identity": "mozzarella_form_factor"}

    id = db.Column(db.Integer, db.ForeignKey("form_factors.id"), primary_key=True)
    default_cooling_technology_id = db.Column(
        db.Integer, db.ForeignKey("mozzarella_cooling_technologies.id"), nullable=True
    )


class MozzarellaBoiling(Boiling):
    __tablename__ = "mozzarella_boilings"
    __mapper_args__ = {"polymorphic_identity": "mozzarella_boiling"}

    id = db.Column(db.Integer, db.ForeignKey("boilings.id"), primary_key=True)
    percent = db.Column(db.Float)
    is_lactose = db.Column(db.Boolean)
    ferment = db.Column(db.String)

    @property
    def boiling_type(self):
        return "salt" if self.line.name == "Пицца чиз" else "water"

    def to_str(self):
        values = [self.percent, self.ferment, "" if self.is_lactose else "без лактозы"]
        values = [str(v) for v in values if v]
        return ", ".join(values)


class MozzarellaBoilingTechnology(BoilingTechnology):
    __tablename__ = "mozzarella_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "mozzarella_boiling_technology"}

    id = db.Column(
        db.Integer, db.ForeignKey("boiling_technologies.id"), primary_key=True
    )
    pouring_time = db.Column(db.Integer)
    soldification_time = db.Column(db.Integer)
    cutting_time = db.Column(db.Integer)
    pouring_off_time = db.Column(db.Integer)
    pumping_out_time = db.Column(db.Integer)
    extra_time = db.Column(db.Integer)

    @staticmethod
    def create_name(line, percent, ferment, is_lactose):
        boiling_name = [percent, ferment, "" if is_lactose else "без лактозы"]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, {}".format(line, boiling_name)


class MozzarellaCoolingTechnology(db.Model):
    __tablename__ = "mozzarella_cooling_technologies"
    id = db.Column(db.Integer, primary_key=True)
    first_cooling_time = db.Column(db.Integer)
    second_cooling_time = db.Column(db.Integer)
    salting_time = db.Column(db.Integer)

    form_factors = db.relationship(
        "MozzarellaFormFactor",
        backref=backref("default_cooling_technology", uselist=False),
    )

    @property
    def time(self):
        values = [self.first_cooling_time, self.second_cooling_time, self.salting_time]
        values = [v if v is not None else np.nan for v in values]
        return np.nansum(values)

    @staticmethod
    def create_name(form_factor_name):
        return "Технология охлаждения форм фактора {}".format(form_factor_name)

    def __repr__(self):
        return "CoolingTechnology({}, {}, {})".format(
            self.first_cooling_time, self.second_cooling_time, self.salting_time
        )
