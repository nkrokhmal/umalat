from dataclasses import dataclass

import pandas as pd


@dataclass
class Order:
    groups: list[str]
    flavoring_agent: str | None
    is_lactose: bool | None

    def order_filter(self, row: pd.Series) -> bool:
        if not row["group"] in self.groups:
            return False

        if self.flavoring_agent is not None and row["flavoring_agent"] != self.flavoring_agent:
            return False

        if self.is_lactose is not None and row["is_lactose"] != self.is_lactose:
            return False

        return True


CREAM_ORDER: list[Order] = [
    Order(["Сливки"], None, False),
    Order(["Сливки"], None, True),
    Order(["Сливки"], None, None),
]
MASCARPONE_ORDER: list[Order] = [
    Order(["Маскарпоне"], None, False),
    Order(["Маскарпоне"], None, True),
    Order(["Маскарпоне"], "Шоколад", True),
    Order(["Маскарпоне"], None, None),
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
    Order(["Кремчиз", "Робиола", "Творожный"], None, None),
]


__all__ = [
    "Order",
    "CREAM_ORDER",
    "MASCARPONE_ORDER",
    "CREAM_CHEESE_ORDER",
]
