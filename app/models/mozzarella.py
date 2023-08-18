from sqlalchemy.orm import backref

from app.enum import LineName
from app.imports.runtime import *

from .basic import SKU, Boiling, BoilingTechnology, FormFactor, Line, backref


class MozzarellaSKU(SKU):
    __tablename__ = "mozzarella_skus"
    __mapper_args__ = {"polymorphic_identity": "mozzarella_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)
    production_by_request = mdb.Column(mdb.Boolean)
    packing_by_request = mdb.Column(mdb.Boolean)


class MozzarellaLine(Line):
    __tablename__ = "mozzarella_lines"
    __mapper_args__ = {"polymorphic_identity": "mozzarella_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    input_ton = mdb.Column(mdb.Integer)
    output_ton = mdb.Column(mdb.Integer)
    pouring_time = mdb.Column(mdb.Integer)
    serving_time = mdb.Column(mdb.Integer)
    melting_speed = mdb.Column(mdb.Integer)
    chedderization_time = mdb.Column(mdb.Integer)

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

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)
    default_cooling_technology_id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("mozzarella_cooling_technologies.id"), nullable=True
    )


class MozzarellaBoiling(Boiling):
    __tablename__ = "mozzarella_boilings"
    __mapper_args__ = {"polymorphic_identity": "mozzarella_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    percent = mdb.Column(mdb.Float)
    is_lactose = mdb.Column(mdb.Boolean)
    ferment = mdb.Column(mdb.String)

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

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)
    pouring_time = mdb.Column(mdb.Integer)
    soldification_time = mdb.Column(mdb.Integer)
    cutting_time = mdb.Column(mdb.Integer)
    pouring_off_time = mdb.Column(mdb.Integer)
    pumping_out_time = mdb.Column(mdb.Integer)
    extra_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(line, percent, ferment, is_lactose):
        boiling_name = [percent, ferment, "" if is_lactose else "без лактозы"]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, {}".format(line, boiling_name)


class MozzarellaCoolingTechnology(mdb.Model):
    __tablename__ = "mozzarella_cooling_technologies"
    id = mdb.Column(mdb.Integer, primary_key=True)
    first_cooling_time = mdb.Column(mdb.Integer)
    second_cooling_time = mdb.Column(mdb.Integer)
    salting_time = mdb.Column(mdb.Integer)

    form_factors = mdb.relationship(
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
