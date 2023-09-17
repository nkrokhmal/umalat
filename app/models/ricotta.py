from app.globals import mdb
from app.models.basic import SKU, Boiling, BoilingTechnology, FormFactor, Line


class RicottaSKU(SKU):
    __tablename__ = "ricotta_skus"
    __mapper_args__ = {"polymorphic_identity": "ricotta_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class RicottaLine(Line):
    __tablename__ = "ricotta_lines"
    __mapper_args__ = {"polymorphic_identity": "ricotta_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    input_kg = mdb.Column(mdb.Integer)


class RicottaFormFactor(FormFactor):
    __tablename__ = "ricotta_form_factors"
    __mapper_args__ = {"polymorphic_identity": "ricotta_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class RicottaBoiling(Boiling):
    __tablename__ = "ricotta_boilings"
    __mapper_args__ = {"polymorphic_identity": "ricotta_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    weight = mdb.Column(mdb.Float)
    flavoring_agent = mdb.Column(mdb.String)
    percent = mdb.Column(mdb.Integer)
    input_kg = mdb.Column(mdb.Integer)
    output_kg = mdb.Column(mdb.Integer)

    @property
    def with_flavor(self) -> bool:
        return self.flavoring_agent != ""

    @property
    def short_display_name(self) -> str:
        return self.flavoring_agent if self.flavoring_agent else "Рикотта"

    def to_str(self) -> str:
        return f"{self.percent}, {self.flavoring_agent}"


class RicottaBoilingTechnology(BoilingTechnology):
    __tablename__ = "ricotta_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "ricotta_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)
    pouring_time = mdb.Column(mdb.Integer)  # Набор сыворотки 6500 кг
    heating_time = mdb.Column(mdb.Integer)  # Нагрев до 90 градусов
    lactic_acid_time = mdb.Column(mdb.Integer)  # молочная кислота/выдерживание
    drain_whey_time = mdb.Column(mdb.Integer)  # слив сыворотки
    dray_ricotta_time = mdb.Column(mdb.Integer)  # слив рикотты
    salting_time = mdb.Column(mdb.Integer)  # посолка/анализ
    pumping_time = mdb.Column(mdb.Integer)  # Перекачивание
    ingredient_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(line: str, percent: float | int, flavoring_agent: str, weight: float) -> str:
        return f"Линия {line}, {percent}, {flavoring_agent}, {weight}"


__all__ = [
    "RicottaBoilingTechnology",
    "RicottaBoiling",
    "RicottaLine",
    "RicottaSKU",
    "RicottaFormFactor",
]
