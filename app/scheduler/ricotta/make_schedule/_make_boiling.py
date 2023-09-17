import warnings

from utils_ak.block_tree import add_push, stack_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.dict import dotdict
from utils_ak.numeric.numeric import custom_round
from utils_ak.pandas import mark_consecutive_groups

from app.scheduler.mascarpone.make_schedule.get_packing_switch_size import get_packing_swith_size


warnings.filterwarnings("ignore")


def _make_boiling(boiling_group_df, **kwargs):
    # - Unfold boiling group params

    sample_row = boiling_group_df.iloc[0]

    boiling_model = sample_row["boiling"]
    technology = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in mascarpone department

    # - Init block maker

    m = BlockMaker(
        "boiling",
        boiling_model=boiling_model,
        **kwargs,
    )

    # - Fill blocks

    pouring = m.row("pouring", size=technology.pouring_time // 5).block
    m.row("heating", size=technology.heating_time // 5, x=pouring.x[0] + 2, push_func=add_push)
    m.row("lactic_acid", size=technology.lactic_acid_time // 5)
    m.row("draw_whey", size=technology.drain_whey_time // 5)
    m.row("draw_ricotta", size=technology.dray_ricotta_time // 5)
    m.row("draw_ricotta_break", size=3)
    m.row("draw_ricotta", size=technology.dray_ricotta_time // 5)
    m.row("salting", size=technology.salting_time // 5)
    m.row("pumping", size=technology.pumping_time // 5)

    # m.row('ingredient', size=technology.ingredient_time // 5)

    return m.root
