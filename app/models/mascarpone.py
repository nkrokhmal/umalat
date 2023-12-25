from app.globals import mdb
from app.models.basic import SKU, Boiling, BoilingTechnology, FormFactor, Line


class MascarponeSKU(SKU):
    __tablename__ = "mascarpone_skus"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class MascarponeLine(Line):
    __tablename__ = "mascarpone_lines"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    params = mdb.Column(mdb.String)

    cream_reconfiguration_short = mdb.Column(mdb.Integer)
    cream_reconfiguration_long = mdb.Column(mdb.Integer)
    creamcheese_reconfiguration = mdb.Column(mdb.Integer)


class MascarponeFormFactor(FormFactor):
    __tablename__ = "mascarpone_form_factors"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class MascarponeBoiling(Boiling):
    __tablename__ = "mascarpone_boilings"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    boiling_type = mdb.Column(mdb.String)
    weight_netto = mdb.Column(mdb.Float)
    is_lactose = mdb.Column(mdb.Boolean, default=False)
    flavoring_agent = mdb.Column(mdb.String)
    percent = mdb.Column(mdb.Float)
    input_kg = mdb.Column(mdb.Float)
    output_constant = mdb.Column(mdb.Float)

    @property
    def dynamic_attributes(self) -> tuple[str, ...]:
        return "output_coeff", "input_kg"

    @property
    def readonly_attributes(self) -> tuple[str, ...]:
        return "boiling_type", "weight_netto", "is_lactose", "flavoring_agent", "percent"

    def to_str(self) -> str:
        return f"{self.percent}, {self.flavoring_agent}"


class MascarponeBoilingTechnology(BoilingTechnology):
    __tablename__ = "mascarpone_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "mascarpone_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)
    weight = mdb.Column(mdb.Integer)

    separation_time = mdb.Column(mdb.Integer)  # blue block сепарирование
    analysis_time = mdb.Column(mdb.Integer)  # white block analysis
    pouring_time = mdb.Column(mdb.Integer)  # yellow block прием
    heating_time = mdb.Column(mdb.Integer)  # orange block Н
    pumping_time = mdb.Column(mdb.Integer)  # brown block П
    salting_time = mdb.Column(mdb.Integer)  # green block посолка, номализация, анализ
    ingredient_time = mdb.Column(mdb.Integer)  # greeen block добавление/нагрев/перемешивание

    line_id = mdb.Column(mdb.Integer, mdb.ForeignKey("mascarpone_lines.id"), nullable=True)

    @property
    def dynamic_attributes(self) -> tuple[str, ...]:
        return (
            "separation_time",
            "analysis_time",
            "pouring_time",
            "heating_time",
            "pumping_time",
            "salting_time",
            "ingredient_time",
        )

    @property
    def readonly_attributes(self) -> tuple[str, str]:
        return "name", "weight"

    @staticmethod
    def create_name(
        line: str,
        weight: float | int,
        percent: float | type,
        cheese_type: str,
        flavoring_agent: str,
        is_lactose: bool,
        input_kg: int,
    ) -> str:
        boiling_name = f"{weight} кг, {percent}, {flavoring_agent}"
        return "Линия {}, {}, {}, {}, {}".format(
            line, cheese_type, boiling_name, "" if is_lactose else "без лактозы", f"{input_kg} kg"
        )


__all__ = [
    "MascarponeBoilingTechnology",
    "MascarponeBoiling",
    "MascarponeLine",
    "MascarponeSKU",
    "MascarponeFormFactor",
]
