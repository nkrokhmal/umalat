from app.globals import mdb
from app.models.basic import SKU, Boiling, BoilingTechnology, FormFactor, Group, Line


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

    def to_str(self) -> str:
        return ", ".join([str(self.percent)])


class ButterBoilingTechnology(BoilingTechnology):
    __tablename__ = "butter_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "butter_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)

    separator_runaway_time = mdb.Column(mdb.Integer)
    pasteurization_time = mdb.Column(mdb.Integer)
    increasing_temperature_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(
        form_factor: str,
        line: str,
        percent: float | int,
        weight: float | int,
        flavoring_agent: str,
        is_lactose: bool,
    ) -> str:
        return "Линия {}, Форм фактор {}, Вес {}, Вкусовая добавка {}, {}, {}".format(
            line,
            form_factor,
            weight,
            flavoring_agent,
            "без лактозы" if not is_lactose else "",
            percent,
        )


__all__ = [
    "ButterBoiling",
    "ButterBoilingTechnology",
    "ButterLine",
    "ButterSKU",
    "ButterFormFactor",
]
