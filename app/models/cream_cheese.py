from . import SKU, Group, Line, FormFactor, Boiling, BoilingTechnology, db


class CreamCheeseSKU(SKU):
    __tablename__ = "cream_cheese_skus"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_skus"}

    id = db.Column(db.Integer, db.ForeignKey("skus.id"), primary_key=True)


class CreamCheeseLine(Line):
    __tablename__ = "cream_cheese_lines"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_lines"}

    id = db.Column(db.Integer, db.ForeignKey("lines.id"), primary_key=True)
    params = db.Column(db.String)


class CreamCheeseFormFactor(FormFactor):
    __tablename__ = "cream_cheese_form_factors"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_form_factor"}

    id = db.Column(db.Integer, db.ForeignKey("form_factors.id"), primary_key=True)


class CreamCheeseBoiling(Boiling):
    __tablename__ = "cream_cheese_boilings"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_boiling"}

    id = db.Column(db.Integer, db.ForeignKey("boilings.id"), primary_key=True)
    percent = db.Column(db.Integer)
    output_ton = db.Column(db.Integer)

    def to_str(self):
        values = [self.percent]
        values = [str(v) for v in values if v]
        return ", ".join(values)


class CreamCheeseBoilingTechnology(BoilingTechnology):
    __tablename__ = "cream_cheese_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "cream_cheese_boiling_technology"}

    id = db.Column(
        db.Integer, db.ForeignKey("boiling_technologies.id"), primary_key=True
    )
    cooling_time = db.Column(db.Integer)
    separation_time = db.Column(db.Integer)
    salting_time = db.Column(db.Integer)
    p_time = db.Column(db.Integer)

    @staticmethod
    def create_name(form_factor, line, percent):
        boiling_name = [percent]
        boiling_name = ", ".join([str(v) for v in boiling_name if v])
        return "Линия {}, Форм фактор {}, {}".format(line, form_factor, boiling_name)


class CreamCheeseFermentator(db.Model):
    __tablename__ = "mascarpone_fermentator"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    line_id = db.Column(db.Integer, db.ForeignKey("mascarpone_lines.id"), nullable=True)
