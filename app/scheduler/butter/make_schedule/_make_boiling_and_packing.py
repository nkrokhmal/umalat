from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.numeric.numeric import custom_round


def _make_boiling_and_packing(boiling_group_df, tank_number):
    sample_row = boiling_group_df.iloc[0]
    boiling_model = sample_row["boiling"]

    m = BlockMaker("boiling", boiling_model=boiling_model, tank_number=tank_number)
    bt = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in butter department

    m.row("separator_runaway", size=bt.separator_runaway_time // 5)
    m.row("pasteurization", size=bt.pasteurization_time // 5)
    m.row("increasing_temperature", size=bt.increasing_temperature_time // 5)

    packing_time = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in boiling_group_df.iterrows()])
    packing_time = int(custom_round(packing_time, 5, "ceil", pre_round_precision=1))

    return m.root, m.create_block(
        "packing", size=(packing_time // 5, 1), boiling_model=boiling_model, tank_number=tank_number
    )
