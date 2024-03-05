from app.globals import mdb
from app.models.basic import SKU, Boiling, BoilingTechnology, FormFactor, Line


class BrynzaSKU(SKU):
    __tablename__ = "brynza_skus"
    __mapper_args__ = {"polymorphic_identity": "brynza_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class BrynzaLine(Line):
    __tablename__ = "brynza_lines"
    __mapper_args__ = {"polymorphic_identity": "brynza_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)


class BrynzaFormFactor(FormFactor):
    __tablename__ = "brynza_form_factors"
    __mapper_args__ = {"polymorphic_identity": "brynza_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class BrynzaBoiling(Boiling):
    __tablename__ = "brynza_boilings"
    __mapper_args__ = {"polymorphic_identity": "brynza_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    name = mdb.Column(mdb.String)
    weight = mdb.Column(mdb.Float)
    percent = mdb.Column(mdb.Integer)
    output_kg = mdb.Column(mdb.Integer)

    def to_str(self) -> str:
        return f"{self.percent}_{self.output_kg}"


class BrynzaBoilingTechnology(BoilingTechnology):
    __tablename__ = "brynza_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "brynza_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)
    boiling_speed = mdb.Column(mdb.Integer)

    pouring_time = mdb.Column(mdb.Integer)
    soldification_time = mdb.Column(mdb.Integer)
    cutting_time = mdb.Column(mdb.Integer)
    pouring_off_time = mdb.Column(mdb.Integer)
    salting_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(
        form_factor: str,
        line: str,
        percent: float | int,
        weight: float | int,
        output_kg: float | int,
    ) -> str:
        return f"Линия {line}, Форм фактор {form_factor}, Вес {weight}, {percent}, {output_kg}"


__all__ = [
    "BrynzaBoiling",
    "BrynzaBoilingTechnology",
    "BrynzaLine",
    "BrynzaSKU",
    "BrynzaFormFactor",
]
