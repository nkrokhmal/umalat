from app.globals import mdb
from app.models.basic import SKU, Boiling, BoilingTechnology, FormFactor, Line


class HalumiSKU(SKU):
    __tablename__ = "halumi_skus"
    __mapper_args__ = {"polymorphic_identity": "halumi_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class HalumiLine(Line):
    __tablename__ = "halumi_lines"
    __mapper_args__ = {"polymorphic_identity": "halumi_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)


class HalumiFormFactor(FormFactor):
    __tablename__ = "halumi_form_factors"
    __mapper_args__ = {"polymorphic_identity": "halumi_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class HalumiBoiling(Boiling):
    __tablename__ = "halumi_boilings"
    __mapper_args__ = {"polymorphic_identity": "halumi_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    weight_netto = mdb.Column(mdb.Float)
    percent = mdb.Column(mdb.Integer)


class HalumiBoilingTechnology(BoilingTechnology):
    __tablename__ = "halumi_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "halumi_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)

    collecting_time = mdb.Column(mdb.Integer)
    coagulation_time = mdb.Column(mdb.Integer)
    pouring_off_time = mdb.Column(mdb.Integer)


__all__ = [
    "HalumiBoiling",
    "HalumiBoilingTechnology",
    "HalumiLine",
    "HalumiSKU",
    "HalumiFormFactor",
]
