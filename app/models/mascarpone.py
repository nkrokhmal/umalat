from sqlalchemy.orm import backref

from . import SKU, Group, Line, FormFactor, Boiling, BoilingTechnology, db


class MascarponeSKU(SKU):
    __tablename__ = "mascarpone_skus"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_skus"}

    id = db.Column(db.Integer, db.ForeignKey("skus.id"), primary_key=True)


class MascarponeLine(Line):
    __tablename__ = "mascarpone_lines"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_lines"}

    id = db.Column(db.Integer, db.ForeignKey("lines.id"), primary_key=True)
    params = db.Column(db.String)
    sourdoughs = db.relationship(
        "MascarponeSourdough", backref=backref("line", uselist=False, lazy="subquery")
    )


class MascarponeFormFactor(FormFactor):
    __tablename__ = "mascarpone_form_factors"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_form_factor"}

    id = db.Column(db.Integer, db.ForeignKey("form_factors.id"), primary_key=True)


class MascarponeBoiling(Boiling):
    __tablename__ = "mascarpone_boilings"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_boiling"}

    id = db.Column(db.Integer, db.ForeignKey("boilings.id"), primary_key=True)
    flavoring_agent = db.Column(db.String)
    percent = db.Column(db.Integer)

    def to_str(self):
        values = [self.percent, self.flavoring_agent]
        values = [str(v) for v in values if v]
        return ", ".join(values)


class MascarponeBoilingTechnology(BoilingTechnology):
    __tablename__ = "mascarpone_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_boiling_technology"}

    id = db.Column(
        db.Integer, db.ForeignKey("boiling_technologies.id"), primary_key=True
    )
    weight = db.Column(db.Integer)
    pouring_time = db.Column(db.Integer)
    heating_time = db.Column(db.Integer)
    adding_lactic_acid_time = db.Column(db.Integer)
    output_ton = db.Column(db.Integer)
    pumping_off_time = db.Column(db.Integer)
    ingredient_time = db.Column(db.Integer)
    line_id = db.Column(db.Integer, db.ForeignKey("mascarpone_lines.id"), nullable=True)

    @staticmethod
    def create_name(line, weight, percent, flavoring_agent):
        boiling_name = ["{} кг".format(weight), percent, flavoring_agent]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, {}".format(line, boiling_name)


boiling_technology_sourdough = db.Table(
    "boiling_technology_sourdough",
    db.Column("sourdough_id", db.Integer, db.ForeignKey("mascarpone_sourdoughs.id"), primary_key=True),
    db.Column("boiling_technology_id", db.Integer, db.ForeignKey("mascarpone_boiling_technologies.id"), primary_key=True),
)


class MascarponeSourdough(db.Model):
    __tablename__ = "mascarpone_sourdoughs"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    name = db.Column(db.String)
    line_id = db.Column(db.Integer, db.ForeignKey("mascarpone_lines.id"), nullable=True)
    boiling_technologies = db.relationship(
        "MascarponeBoilingTechnology", secondary=boiling_technology_sourdough, backref=backref("sourdoughs", lazy="subquery")
    )

    def to_str(self):
        return f"{self.name}, {self.output_ton}"

