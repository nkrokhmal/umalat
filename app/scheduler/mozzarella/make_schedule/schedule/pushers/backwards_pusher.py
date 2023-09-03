from utils_ak.block_tree import IterativePusher


class BackwardsPusher(IterativePusher):
    def __init__(self, max_period):
        super().__init__()
        self.max_period = max_period

    def add(self, period):
        self.block.props.update(
            x=[
                self.block.props["x_rel"][0] + period,
                self.block.x[1],
            ]
        )

    def init(self):
        self.add(self.max_period)

    def update(self, results):
        self.add(-1)
