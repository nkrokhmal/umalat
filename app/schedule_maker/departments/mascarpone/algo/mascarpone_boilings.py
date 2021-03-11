from utils_ak.block_tree import *
from utils_ak.iteration import *
from utils_ak.builtin import *

from app.schedule_maker.models import *


def make_mascorpone_boiling(boiling_group_df):
    boiling_model = boiling_group_df.iloc[0]["sku"].made_from_boilings[0]
    boiling_id = boiling_group_df.iloc[0]["boiling_id"]
    maker, make = init_block_maker(
        "boiling", boiling_model=boiling_model, boiling_id=boiling_id
    )
    bt = boiling_model.boiling_technology

    with make("boiling_process"):
        make("pouring", size=(bt.heating_time // 5, 0))
        make("heating", size=(bt.heating_time // 5, 0))
        make("waiting", size=[0, 0])
        make("adding_lactic_acid", size=(bt.heating_time // 5, 0))
        make("separation", size=(bt.heating_time // 5, 0))
    with make("packing_process", x=(maker.root["boiling_process"].x[0], 0)):
        make("N", size=(2, 0))
        make("P", size=(2, 0))

        packing_start = (
            maker.root["packing_process"]["P"].props.relative_props["x"][0] + 1
        )

        packing_time = sum(
            [
                row["kg"] / row["sku"].packing_speed * 60
                for i, row in boiling_group_df.iterrows()
            ]
        )
        packing_time = int(custom_round(packing_time, 5, "ceil"))

        make(
            "packing",
            x=(packing_start, 0),
            size=(packing_time // 5, 0),
            push_func=add_push,
        )
    return maker.root


def make_mascarpone_boiling_group(boiling_group_df1, boiling_group_df2):
    # todo: check that only one boiling_model
    boiling_model = boiling_group_df1.iloc[0]["sku"].made_from_boilings[0]

    validator = ClassValidator(window=3)

    def validate(b1, b2):
        validate_disjoint_by_axis(
            b1["packing_process"]["packing"], b2["packing_process"]["packing"]
        )
        # just in case, not needed in reality
        validate_disjoint_by_axis(
            b1["boiling_process"]["separation"], b2["boiling_process"]["separation"]
        )
        assert (
            b2["boiling_process"]["pouring"].x[0]
            >= b1["boiling_process"]["pouring"].y[0]
        )

    validator.add("boiling", "boiling", validate)

    maker, make = init_block_maker(
        "mascarpone_boiling_group", boiling_model=boiling_model
    )

    b1 = make_mascorpone_boiling(boiling_group_df1)
    b2 = make_mascorpone_boiling(boiling_group_df2)
    for b in [b1, b2]:
        push(
            maker.root,
            b,
            push_func=AxisPusher(start_from="last_beg"),
            validator=validator,
        )
    # fix waiting time
    waiting_size = (
        b2["boiling_process"]["pouring"].x[0] - b1["boiling_process"]["pouring"].y[0]
    )

    for b in [b2["boiling_process"]]:
        b.props.update(x=(b.props["x_rel"][0] - waiting_size, 0))
    for key in ["adding_lactic_acid", "separation"]:
        b = b2["boiling_process"][key]
        b.props.update(x=(b.props["x_rel"][0] + waiting_size, 0))
    b2["boiling_process"]["waiting"].props.update(size=(waiting_size, 0))
    return maker.root
