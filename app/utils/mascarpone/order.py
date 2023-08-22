from dataclasses import dataclass

import pandas as pd


@dataclass
class Order:
    groups: list[str]
    flavoring_agent: str | None
    is_lactose: bool

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
    Order(["Сливки"], None, False),
    Order(["Сливки"], None, True),
]
MASCARPONE_ORDER: list[Order] = [
    Order(["Маскарпоне"], None, False),
    Order(["Маскарпоне"], None, True),
    Order(["Маскарпоне"], "Шоколад", True),
]
CREAM_CHEESE_ORDER: list[Order] = [
    Order(["Кремчиз"], None, False),
    Order(["Кремчиз"], None, True),
    Order(["Кремчиз"], "Паприка", True),
    Order(["Кремчиз"], "Томаты", True),
    Order(["Кремчиз"], "Травы", True),
    Order(["Кремчиз"], "Огурец", True),
    Order(["Творожный"], None, True),
    Order(["Робиола"], None, True),
]


__all__ = [
    "Order",
    "CREAM_ORDER",
    "MASCARPONE_ORDER",
    "CREAM_CHEESE_ORDER",
]
