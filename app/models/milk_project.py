from app.globals import mdb
from app.models.basic import SKU, Boiling, BoilingTechnology, FormFactor, Line


class MilkProjectSKU(SKU):
    __tablename__ = "milk_project_skus"
    __mapper_args__ = {"polymorphic_identity": "milk_project_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)


class MilkProjectLine(Line):
    __tablename__ = "milk_project_lines"
    __mapper_args__ = {"polymorphic_identity": "milk_project_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    water_collecting_time = mdb.Column(mdb.Integer)
    equipment_check_time = mdb.Column(mdb.Integer)


class MilkProjectFormFactor(FormFactor):
    __tablename__ = "milk_project_form_factors"
    __mapper_args__ = {"polymorphic_identity": "milk_project_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class MilkProjectBoiling(Boiling):
    __tablename__ = "milk_project_boilings"
    __mapper_args__ = {"polymorphic_identity": "milk_project_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    name = mdb.Column(mdb.String)
    weight_netto = mdb.Column(mdb.Float)
    output_kg = mdb.Column(mdb.Integer)
    percent = mdb.Column(mdb.Integer)

    # todo later: delete [@marklidenberg]
    equipment_check_time = mdb.Column(mdb.Integer)

    def to_str(self) -> str:
        return str(self.percent)


class MilkProjectBoilingTechnology(BoilingTechnology):
    __tablename__ = "milk_project_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "milk_project_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)

    mixture_collecting_time = mdb.Column(mdb.Integer)
    processing_time = mdb.Column(mdb.Integer)

    # todo later: rename [@marklidenberg]
    red_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(
        form_factor: str,
        line: str,
        percent: float | int,
        weight: float | int,
    ) -> str:
        boiling_name = ", ".join([str(percent)])
        return "Линия {}, Форм фактор {}, Вес {}, {}".format(
            line,
            form_factor,
            weight,
            boiling_name,
        )


__all__ = [
    "MilkProjectBoiling",
    "MilkProjectBoilingTechnology",
    "MilkProjectLine",
    "MilkProjectFormFactor",
    "MilkProjectSKU",
]
