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
    weight = db.Column(db.Integer)


class MascarponeBoilingTechnology(BoilingTechnology):
    __tablename__ = "mascarpone_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_boiling_technology"}

    id = db.Column(
        db.Integer, db.ForeignKey("boiling_technologies.id"), primary_key=True
    )
    pouring_time = db.Column(db.Integer)
    heating_time = db.Column(db.Integer)
    adding_lactic_acid_time = db.Column(db.Integer)
    separation_time = db.Column(db.Integer)

    @staticmethod
    def create_name(line, weight, percent, flavoring_agent):
        boiling_name = ["{} кг".format(weight), percent, flavoring_agent]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, {}".format(line, boiling_name)
