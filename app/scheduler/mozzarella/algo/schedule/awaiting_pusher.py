from utils_ak.block_tree import *
from utils_ak.builtin import listify


class AwaitingPusher(IterativePusher):
    def __init__(self, max_awaiting_period):
        super().__init__()
        self.max_awaiting_period = max_awaiting_period

    def add(self, period):
        # move boiling block left
        # logger.debug('Boiling', boiling_id=self.block.props['boiling_id'])
        # logger.debug('Before', x=self.block.x[0], packings=[packing.x[0] for packing in listify(self.block['melting_and_packing']['packing'])])

        self.block.props.update(
            x=[self.block.props["x_rel"][0] - period, self.block.x[1]]
        )

        for collecting in listify(self.block["melting_and_packing"]["collecting"]):
            collecting.props.update(
                x=[collecting.props["x_rel"][0] + period, collecting.x[1]]
            )

        for packing in listify(self.block["melting_and_packing"]["packing"]):
            packing.props.update(x=[packing.props["x_rel"][0] + period, packing.x[1]])
        # logger.debug('After', x=self.block.x[0], packings=[packing.x[0] for packing in listify(self.block['melting_and_packing']['packing'])])

    def init(self):
        self.add(self.max_awaiting_period)

    def update(self, results):
        self.add(-1)
