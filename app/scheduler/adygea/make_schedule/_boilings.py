from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify


def make_boiling(boiling_model, batch_id, boiler_num, group_name, pair_num):
    m = BlockMaker(
        "boiling",
        boiling_model=boiling_model,
        boiling_id=batch_id,
        boiler_num=boiler_num,
        group_name=group_name,
        pair_num=pair_num,
    )

    bt = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in ricotta department

    m.push_row("collecting", size=bt.collecting_time // 5)
    m.push_row("coagulation", size=bt.coagulation_time // 5)
    m.push_row("pouring_off", size=bt.pouring_off_time // 5)

    return m.root


def make_cleaning(size, **kwargs):
    m = BlockMaker("cleaning", **kwargs)
    m.push_row(f"cleaning", size=size)
    return m.root


def make_preparation(size, **kwargs):
    m = BlockMaker("preparation", size=(size, 0), **kwargs)
    return m.root


def make_lunch(size, **kwargs):
    m = BlockMaker("lunch", **kwargs)
    m.push_row(f"lunch", size=size)
    return m.root
