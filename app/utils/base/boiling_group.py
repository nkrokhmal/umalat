import itertools

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BoilingGroup:
    weight: float
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


class BoilingsHandler(ABC):
    def __init__(self):
        self.boilings: list[BoilingGroup] = []
        self.boiling_id: int = 0

    @property
    def boiling_groups(self) -> list[dict]:
        return list(itertools.chain.from_iterable(boiling.skus for boiling in self.boilings))

    @abstractmethod
    def handle_group(self, skus: list[dict], max_weight: float, weight_key: str = "plan") -> None:
        ...
