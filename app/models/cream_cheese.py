from sqlalchemy.orm import backref

from app.imports.runtime import *

from .basic import SKU, Boiling, BoilingTechnology, FormFactor, Group, Line


class CreamCheeseSKU(SKU):
    __tablename__ = "cream_cheese_skus"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class CreamCheeseLine(Line):
    __tablename__ = "cream_cheese_lines"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    params = mdb.Column(mdb.String)


class CreamCheeseFormFactor(FormFactor):
    __tablename__ = "cream_cheese_form_factors"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class CreamCheeseBoiling(Boiling):
    __tablename__ = "cream_cheese_boilings"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    weight_netto = mdb.Column(mdb.Float)
    percent = mdb.Column(mdb.Integer)
    is_lactose = mdb.Column(mdb.Boolean, default=False)
    flavoring_agent = mdb.Column(mdb.String)
    output_ton = mdb.Column(mdb.Integer)

    def to_str(self):
        values = [self.percent]
        values = [str(v) for v in values if v]
        return ", ".join(values)


class CreamCheeseBoilingTechnology(BoilingTechnology):
    __tablename__ = "cream_cheese_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)
    cooling_time = mdb.Column(mdb.Integer)
    separation_time = mdb.Column(mdb.Integer)
    salting_time = mdb.Column(mdb.Integer)
    p_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(form_factor, line, percent, weight, flavoring_agent, is_lactose):
        boiling_name = [percent]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, Форм фактор {}, Вес {}, {}, {}, {}".format(
            line, form_factor, weight, boiling_name, flavoring_agent, "" if is_lactose else "без лактозы"
        )


class CreamCheeseFermentator(mdb.Model):
    __tablename__ = "mascarpone_fermentator"

    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)
    line_id = mdb.Column(mdb.Integer, mdb.ForeignKey("mascarpone_lines.id"), nullable=True)
