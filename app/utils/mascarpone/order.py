from dataclasses import dataclass

import pandas as pd


@dataclass
class Order:
    groups: list[str]
    flavoring_agent: str | None
    is_lactose: bool
    max_weight: int

    @property
    def flavoring_agent_str(self):
        return self.flavoring_agent if self.flavoring_agent is not None else ""

    def order_filter(self, row: pd.Series) -> bool:
        if not row["group"] in self.groups:
            return False

        if row["flavoring_agent"] != self.flavoring_agent_str:
            return False

        if row["is_lactose"] != self.is_lactose:
            return False

        return True


CREAM_ORDER: list[Order] = [
    Order(["Сливки"], None, False, 800),
    Order(["Сливки"], None, True, 800),
]
MASCARPONE_ORDER: list[Order] = [
    Order(["Маскарпоне"], None, False, 8000),
    Order(["Маскарпоне"], None, True, 8000),
    Order(["Маскарпоне"], "Шоколад", True, 8000),
]
CREAM_CHEESE_ORDER: list[Order] = [
    Order(["Кремчиз"], None, False, 8000),
    Order(["Кремчиз"], None, True, 8000),
    Order(["Кремчиз"], "Паприка", True, 8000),
    Order(["Кремчиз"], "Томаты", True, 8000),
    Order(["Кремчиз"], "Травы", True, 8000),
    Order(["Кремчиз"], "Огурец", True, 8000),
    Order(["Творожный"], None, True, 8000),
    Order(["Робиола"], None, True, 8000),
]


__all__ = [
    "Order",
    "CREAM_ORDER",
    "MASCARPONE_ORDER",
    "CREAM_CHEESE_ORDER",
]
