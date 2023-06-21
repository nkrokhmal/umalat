from utils_ak.block_tree import *
from utils_ak.builtin import listify


class DrenatorShrinkingPusher(IterativePusher):
    def __init__(self, max_period):
        super().__init__()
        self.max_period = max_period

    def add(self, period):
        self.block["drenator"].props.update(
            x=[
                self.block["drenator"].props["x_rel"][0] + period,
                self.block["drenator"].x[1],
            ]
        )

        self.block["melting_and_packing"].props.update(
            x=[
                self.block["melting_and_packing"].props["x_rel"][0] + period,
                self.block["melting_and_packing"].x[1],
            ]
        )

    def init(self):
        self.add(self.max_period)

    def update(self, results):
        self.add(1)
