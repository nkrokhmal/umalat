from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.numeric.numeric import custom_round

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.butter.to_boiling_plan import to_boiling_plan


def _make_boiling_and_packing(boiling_group_df, tank_number):
    # - Get sample model

    sample_row = boiling_group_df.iloc[0]
    boiling_model = sample_row["boiling"]

    # - Build boiling block

    m = BlockMaker(
        "boiling",
        # - metadata, will be used later in frontend
        boiling_model=boiling_model,
        tank_number=tank_number,
    )
    bt = delistify(
        boiling_model.boiling_technologies, single=True
    )  # there is only one boiling technology is for every boiling model in butter department

    m.row("separator_runaway", size=bt.separator_runaway_time // 5)
    m.row("pasteurization", size=bt.pasteurization_time // 5)
    m.row("increasing_temperature", size=bt.increasing_temperature_time // 5)

    boiling_block = m.root

    # - Build packing block

    _packing_time = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in boiling_group_df.iterrows()])
    _packing_time = int(custom_round(_packing_time, 5, "ceil", pre_round_precision=1))
    packing_block = m.create_block(
        "packing",
        size=(_packing_time // 5, 1),
        # - metadata
        boiling_model=boiling_model,
        tank_number=tank_number,
    )

    # - Return tuple of boiling and packing block

    return boiling_block, packing_block


def test():
    a, b = _make_boiling_and_packing(
        boiling_group_df=to_boiling_plan(
            str(get_repo_path() / "app/data/static/samples/by_department/butter/2023-09-03 План по варкам масло.xlsx")
        ),
        tank_number=1,
    )
    print(a)
    print(b)


if __name__ == "__main__":
    test()
