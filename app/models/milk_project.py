from app.imports.runtime import *

from sqlalchemy.orm import backref

from .basic import SKU, Group, Line, FormFactor, Boiling, BoilingTechnology


class MilkProjectSKU(SKU):
    __tablename__ = "milk_project_skus"
    __mapper_args__ = {"polymorphic_identity": "milk_project_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class MilkProjectLine(Line):
    __tablename__ = "milk_project_lines"
    __mapper_args__ = {"polymorphic_identity": "milk_project_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)


class MilkProjectFormFactor(FormFactor):
    __tablename__ = "milk_project_form_factors"
    __mapper_args__ = {"polymorphic_identity": "milk_project_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class MilkProjectBoiling(Boiling):
    __tablename__ = "milk_project_boilings"
    __mapper_args__ = {"polymorphic_identity": "milk_project_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    weight_netto = mdb.Column(mdb.Float)
    output_ton = mdb.Column(mdb.Integer)
    percent = mdb.Column(mdb.Integer)

    def to_str(self):
        values = [self.percent]
        values = [str(v) for v in values if v]
        return ", ".join(values)


class MilkProjectBoilingTechnology(BoilingTechnology):
    __tablename__ = "milk_project_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "milk_project_boiling_technology"}

    id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True
    )

    water_collecting_time = mdb.Column(mdb.Integer)
    mixture_collecting_time = mdb.Column(mdb.Integer)
    processing_time = mdb.Column(mdb.Integer)
    # todo: rename
    red_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(form_factor, line, percent, weight,):
        boiling_name = [percent]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, Форм фактор {}, Вес {}, {}".format(
            line, form_factor, weight, boiling_name,
        )

