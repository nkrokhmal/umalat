from utils_ak.block_tree import BlockMaker
from datetime import datetime


def create_schedule_skeleton_block_maker(date: datetime):
    m = BlockMaker("schedule")
    m.root.props.update(date=date)
    m.block("master")
    m.block("extra")
    m.block("extra_packings")

    with m.block("shifts"):
        m.block("cheese_makers")
        m.block("water_meltings")
        m.block("water_packings")
        m.block("salt_meltings")
        m.block("salt_packings")

    return m
