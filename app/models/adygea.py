from app.imports.runtime import *

from sqlalchemy.orm import backref

from app.models.basic import SKU, Group, Line, FormFactor, Boiling, BoilingTechnology


class AdygeaSKU(SKU):
    __tablename__ = "adygea_skus"
    __mapper_args__ = {"polymorphic_identity": "adygea_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class AdygeaLine(Line):
    __tablename__ = "adygea_lines"
    __mapper_args__ = {"polymorphic_identity": "adygea_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    lunch_time = mdb.Column(mdb.Integer)
    preparation_time = mdb.Column(mdb.Integer)


class AdygeaFormFactor(FormFactor):
    __tablename__ = "adygea_form_factors"
    __mapper_args__ = {"polymorphic_identity": "adygea_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class AdygeaBoiling(Boiling):
    __tablename__ = "adygea_boilings"
    __mapper_args__ = {"polymorphic_identity": "adygea_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    name = mdb.Column(mdb.String)
    weight_netto = mdb.Column(mdb.Float)
    input_kg = mdb.Column(mdb.Integer)
    output_kg = mdb.Column(mdb.Integer)
    percent = mdb.Column(mdb.Integer)

    def to_str(self):
        values = [self.percent]
        values = [str(v) for v in values if v]
        return ", ".join(values)


class AdygeaBoilingTechnology(BoilingTechnology):
    __tablename__ = "adygea_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "adygea_boiling_technology"}

    id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True
    )

    collecting_time = mdb.Column(mdb.Integer)
    coagulation_time = mdb.Column(mdb.Integer)
    pouring_off_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(form_factor, line, percent, weight,):
        boiling_name = [percent]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, Форм фактор {}, Вес {}, {}".format(
            line, form_factor, weight, boiling_name,
        )

