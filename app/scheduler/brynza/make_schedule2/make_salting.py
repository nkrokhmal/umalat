from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.builtin.collection import delistify
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.numeric import custom_round

from app.globals import db
from app.models import BrynzaBoiling, BrynzaSKU


def make_salting(boiling_id: int, **props):

    # - Init block maker

    m = BlockMaker("root")

    # - Get models

    skus = [sku for sku in db.session.query(BrynzaSKU).all() if sku.group.name == "Брынза"]

    if not skus:
        raise Exception("No brynza skus found")

    sku = skus[0]

    boilings = [bm for bm in db.session.query(BrynzaBoiling).all() if sku in bm.skus]

    if not boilings:
        raise Exception("No brynza boiling models found")

    boiling = boilings[0]

    boiling_technology = boiling.boiling_technologies[0]

    # - Make brynza boiling

    with m.push("salting", boiling_id=boiling_id, **props):
        m.push_row("main", size=boiling_technology.salting_time // 5)

    return m.root["salting"]


def test():
    print(make_salting(1))


if __name__ == "__main__":
    test()
