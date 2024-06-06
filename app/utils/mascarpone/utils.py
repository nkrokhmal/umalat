from copy import deepcopy

import flask

from app.utils.base.boiling_group import BoilingGroup, BoilingsHandler
from app.utils.parse_remainings import cast_sku_name


class MascarponeBoilingsHandler(BoilingsHandler):
    def __init__(
        self,
        check_boilings: bool = False,
        use_boiling_weight: bool = False,
    ):
        super().__init__()
        self.check_boiling, self.use_boiling_weight = check_boilings, use_boiling_weight

    @staticmethod
    def get_input_kg(sku_name: str) -> int:
        boiling = cast_sku_name(sku_name).made_from_boilings[0]
        return round(boiling.input_kg * boiling.output_coeff, -1)

    @staticmethod
    def check_boiling_kg(boiling: BoilingGroup) -> None:
        if boiling.leftovers > 10:
            try:
                flask.flash(
                    flask.Markup(f'В варке с SKU {boiling.skus[-1]["sku_name"]} не хватает {boiling.leftovers} кг'),
                    "warning",
                )
            except Exception as e:
                if "Working outside of request context" not in str(e):
                    # this error happens on local development
                    raise

    def handle_group(self, skus: list[dict], max_weight: float, weight_key: str = "plan", **kwargs) -> None:
        if len(skus) == 0:
            return

        if self.use_boiling_weight:
            max_weight = self.get_input_kg(skus[0]["sku_name"])
        boiling = BoilingGroup(max_weight, id=self.boiling_id)

        for sku in skus:
            new_max_weight = max_weight if not self.use_boiling_weight else self.get_input_kg(sku["sku_name"])

            if abs(new_max_weight - max_weight) > 10:
                if self.check_boiling:
                    self.check_boiling_kg(boiling)

                max_weight = new_max_weight
                self.boilings.append(boiling)
                self.boiling_id += 1
                boiling = BoilingGroup(max_weight, id=self.boiling_id)

            while sku[weight_key] > 0:
                if boiling.is_full:
                    self.boilings.append(boiling)
                    self.boiling_id += 1
                    boiling = BoilingGroup(max_weight, id=self.boiling_id)
                else:
                    weight = min(sku[weight_key], boiling.leftovers)
                    group_sku = deepcopy(sku)
                    group_sku[weight_key] = weight
                    boiling.add_sku(group_sku, weight_key=weight_key)
                    sku[weight_key] -= weight

        if self.check_boiling:
            self.check_boiling_kg(boiling)

        if boiling.leftovers != max_weight:
            self.boilings.append(boiling)
            self.boiling_id += 1


__all__ = ["MascarponeBoilingsHandler"]
