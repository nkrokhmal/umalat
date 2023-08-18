from sqlalchemy.orm import backref

from app.imports.runtime import *

from .basic import SKU, Boiling, BoilingTechnology, FormFactor, Group, Line


class ButterSKU(SKU):
    __tablename__ = "butter_skus"
    __mapper_args__ = {"polymorphic_identity": "butter_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class ButterLine(Line):
    __tablename__ = "butter_lines"
    __mapper_args__ = {"polymorphic_identity": "butter_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    preparing_time = mdb.Column(mdb.Integer)
    displacement_time = mdb.Column(mdb.Integer)
    output_kg = mdb.Column(mdb.Integer)
    cleaning_time = mdb.Column(mdb.Integer)
    boiling_volume = mdb.Column(mdb.Integer)


class ButterFormFactor(FormFactor):
    __tablename__ = "butter_form_factors"
    __mapper_args__ = {"polymorphic_identity": "butter_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class ButterBoiling(Boiling):
    __tablename__ = "butter_boilings"
    __mapper_args__ = {"polymorphic_identity": "butter_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    weight_netto = mdb.Column(mdb.Float)
    flavoring_agent = mdb.Column(mdb.String)
    is_lactose = mdb.Column(mdb.Boolean)
    percent = mdb.Column(mdb.Integer)

    def to_str(self):
        values = [self.percent]
        values = [str(v) for v in values if v]
        return ", ".join(values)


class ButterBoilingTechnology(BoilingTechnology):
    __tablename__ = "butter_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "butter_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)

    separator_runaway_time = mdb.Column(mdb.Integer)
    pasteurization_time = mdb.Column(mdb.Integer)
    increasing_temperature_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(form_factor, line, percent, weight, flavoring_agent, is_lactose):
        boiling_name = [percent]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, Форм фактор {}, Вес {}, Вкусовая добавка {}, {}, {}".format(
            line,
            form_factor,
            weight,
            flavoring_agent,
            "без лактозы" if not is_lactose else "",
            boiling_name,
        )
