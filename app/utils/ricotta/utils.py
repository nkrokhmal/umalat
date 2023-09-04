import itertools
import typing as tp

from copy import deepcopy
from dataclasses import dataclass

from app.utils.base.boiling_group import BoilingGroup, BoilingsHandler


@dataclass
class RicottaBoilingGroup(BoilingGroup):
    count: int = 1

    @property
    def is_single_instance(self) -> bool:
        return len(self.skus) == 1


class RicottaBoilingsHandler(BoilingsHandler):
    def __init__(self):
        super().__init__()

    @property
    def boiling_groups(self) -> list[dict]:
        result: list[dict] = []
        for group in self.boilings:
            for sku in group.skus:
                result.append((lambda d: d.update({"boiling_count": group.count}) or d)(sku.copy()))
        return result

    def handle_group(self, skus: list[dict], max_weight: float, weight_key: str = "plan") -> None:
        boiling = RicottaBoilingGroup(max_weight, id=self.boiling_id)
        for sku in skus:
            while sku[weight_key] > 0:
                if boiling.is_full:
                    self.boilings.append(boiling)
                    self.boiling_id += 1
                    boiling = RicottaBoilingGroup(max_weight, id=self.boiling_id)

                else:
                    weight = min(sku[weight_key], boiling.leftovers)
                    group_sku = deepcopy(sku)
                    group_sku[weight_key] = weight
                    boiling.add_sku(group_sku)
                    sku[weight_key] -= weight

        if boiling.leftovers != max_weight:
            self.boilings.append(boiling)
            self.boiling_id += 1

        self.boilings = list(self.merge_boilings())

    def merge_boilings(self) -> tp.Generator[RicottaBoilingGroup, None, None]:
        boiling_group: RicottaBoilingGroup | None = None

        for boiling in self.boilings:
            if not boiling.is_single_instance or not boiling.is_full:
                if boiling_group is not None:
                    yield boiling_group
                yield boiling
                boiling_group = None

            elif boiling_group is None:
                boiling_group = boiling

            else:
                boiling_group.count += 1

        if boiling_group is not None:
            yield boiling_group


__all__ = ["RicottaBoilingsHandler"]
