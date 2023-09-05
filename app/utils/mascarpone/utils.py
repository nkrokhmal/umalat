from copy import deepcopy

from app.utils.base.boiling_group import BoilingGroup, BoilingsHandler


class MascarponeBoilingsHandler(BoilingsHandler):
    def __init__(self):
        super().__init__()

    def handle_group(self, skus: list[dict], max_weight: float, weight_key: str = "plan") -> None:
        boiling = BoilingGroup(max_weight, id=self.boiling_id)
        for sku in skus:
            while sku[weight_key] > 0:
                if boiling.is_full:
                    self.boilings.append(boiling)
                    self.boiling_id += 1
                    boiling = BoilingGroup(max_weight, id=self.boiling_id)

                else:
                    weight = min(sku[weight_key], boiling.leftovers)
                    group_sku = deepcopy(sku)
                    group_sku[weight_key] = weight
                    boiling.add_sku(group_sku)
                    sku[weight_key] -= weight

        if boiling.leftovers != max_weight:
            self.boilings.append(boiling)
            self.boiling_id += 1


__all__ = ["MascarponeBoilingsHandler"]
