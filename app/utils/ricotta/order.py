from dataclasses import dataclass

import pandas as pd


@dataclass
class Order:
    percent: float | None
    flavoring_agent: str | None

    @property
    def flavoring_agent_str(self):
        return self.flavoring_agent if self.flavoring_agent is not None else ""

    def order_filter(self, row: pd.Series) -> bool:
        if self.percent is not None and not row["percent"] != self.percent:
            return False

        if row["flavoring_agent"] != self.flavoring_agent_str:
            return False

        return True


RICOTTA_ORDERS: list[Order] = [
    Order(25, None),
    Order(30, None),
    Order(35, None),
    Order(40, None),
    Order(45, None),
    Order(50, None),
    Order(None, "Ваниль"),
    Order(None, "Шоколад"),
    Order(None, "Шоколад-орех"),
    Order(None, "Вишня"),
    Order(None, "Мед"),
]


__all__ = [
    "Order",
    "RICOTTA_ORDERS",
]
