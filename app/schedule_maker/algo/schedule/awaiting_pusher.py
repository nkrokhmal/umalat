from utils_ak.block_tree import *
from utils_ak.builtin import listify


class AwaitingPusher(IterativePusher):
    def __init__(self, max_awaiting_period=12):
        super().__init__()
        self.max_awaiting_period = max_awaiting_period

    def add(self, period):
        # move boiling block left
        self.block.props.update(x=[self.block.x[0] - period, self.block.x[1]])

        for packing in listify(self.block['melting_and_packing']['packing']):
            packing.props.update(x=[packing.x[0] + period, packing.x[1]])

    def init(self):
        self.add(self.max_awaiting_period)

    def update(self, results):
        self.add(-1)
