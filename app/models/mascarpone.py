from app.imports.runtime import *

from .basic import SKU, Group, Line, FormFactor, Boiling, BoilingTechnology


class MascarponeSKU(SKU):
    __tablename__ = "mascarpone_skus"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class MascarponeLine(Line):
    __tablename__ = "mascarpone_lines"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    params = mdb.Column(mdb.String)
    sourdoughs = mdb.relationship(
        "MascarponeSourdough", backref=backref("line", uselist=False, lazy="subquery")
    )


class MascarponeFormFactor(FormFactor):
    __tablename__ = "mascarpone_form_factors"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class MascarponeBoiling(Boiling):
    __tablename__ = "mascarpone_boilings"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    flavoring_agent = mdb.Column(mdb.String)
    percent = mdb.Column(mdb.Integer)

    def to_str(self):
        values = [self.percent, self.flavoring_agent]
        values = [str(v) for v in values if v]
        return ", ".join(values)


class MascarponeBoilingTechnology(BoilingTechnology):
    __tablename__ = "mascarpone_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_boiling_technology"}

    id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True
    )
    weight = mdb.Column(mdb.Integer)
    pouring_time = mdb.Column(mdb.Integer)
    heating_time = mdb.Column(mdb.Integer)
    adding_lactic_acid_time = mdb.Column(mdb.Integer)
    output_ton = mdb.Column(mdb.Integer)
    pumping_off_time = mdb.Column(mdb.Integer)
    ingredient_time = mdb.Column(mdb.Integer)
    line_id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("mascarpone_lines.id"), nullable=True
    )

    @staticmethod
    def create_name(line, weight, percent, flavoring_agent):
        boiling_name = ["{} кг".format(weight), percent, flavoring_agent]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, {}".format(line, boiling_name)


boiling_technology_sourdough = mdb.Table(
    "boiling_technology_sourdough",
    mdb.Column(
        "sourdough_id",
        mdb.Integer,
        mdb.ForeignKey("mascarpone_sourdoughs.id"),
        primary_key=True,
    ),
    mdb.Column(
        "boiling_technology_id",
        mdb.Integer,
        mdb.ForeignKey("mascarpone_boiling_technologies.id"),
        primary_key=True,
    ),
)


class MascarponeSourdough(mdb.Model):
    __tablename__ = "mascarpone_sourdoughs"

    id = mdb.Column(mdb.Integer, primary_key=True)
    number = mdb.Column(mdb.Integer)
    name = mdb.Column(mdb.String)
    line_id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("mascarpone_lines.id"), nullable=True
    )
    boiling_technologies = mdb.relationship(
        "MascarponeBoilingTechnology",
        secondary=boiling_technology_sourdough,
        backref=backref("sourdoughs", lazy="subquery"),
    )

    def to_str(self):
        return f"{self.name}, {self.output_ton}"
