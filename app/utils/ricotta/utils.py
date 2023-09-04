import itertools
import typing as tp

from copy import deepcopy
from dataclasses import dataclass


@dataclass
class BoilingGroup:
    weight: float
    count: int = 0
    id: int = 0

    def __post_init__(self) -> None:
        self.skus: list[dict] = []
        self.leftovers: float = self.weight

    def add_sku(self, sku: dict, weight_key="plan") -> None:
        if sku[weight_key] > self.leftovers:
            raise ValueError("Can't add new SKU, the boiling weight has been exceeded")

        sku.update(dict(id=self.id))
        self.skus.append(sku)
        self.leftovers -= sku[weight_key]

    @property
    def is_full(self) -> bool:
        return -1e-10 <= self.leftovers <= 1e-10

    @property
    def is_single_instance(self) -> bool:
        return len(self.skus) == 1


class BoilingsHandler:
    def __init__(self):
        self.boilings: list[BoilingGroup] = []
        self.boiling_id: int = 0

    @property
    def boiling_groups(self) -> list[dict]:
        return list(itertools.chain.from_iterable(boiling.skus for boiling in self.boilings))

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

        self.boilings = list(self.merge_boilings())

    def merge_boilings(self) -> tp.Generator[BoilingGroup, None, None]:
        boiling_group: BoilingGroup | None = None

        for boiling in self.boilings:
            if not boiling.is_single_instance:
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


__all__ = ["BoilingGroup", "BoilingsHandler"]
