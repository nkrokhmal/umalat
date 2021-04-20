from utils_ak.block_tree import *
from utils_ak.iteration import *
from utils_ak.builtin import *

from app.schedule_maker.models import *


def make_mascorpone_boiling(boiling_group_df, **props):
    sku = boiling_group_df.iloc[0]["sku"]
    is_cream = boiling_group_df.iloc[0]["is_cream"]
    if is_cream:
        sourdough = None
    else:
        sourdough = int(boiling_group_df.iloc[0]["sourdough"])
    boiling_id = boiling_group_df.iloc[0]["boiling_id"]

    boiling_models = sku.made_from_boilings
    boiling_model = delistify(boiling_models, single=True)

    maker, make = init_block_maker(
        "boiling",
        boiling_model=boiling_model,
        boiling_id=boiling_id,
        is_cream=is_cream,
        **props,
    )

    if not is_cream:
        boiling_technologies = [
            boiling_technology
            for boiling_technology in boiling_model.boiling_technologies
            if cast_model(MascarponeSourdough, sourdough)
            in boiling_technology.sourdoughs
        ]
    else:
        boiling_technologies = boiling_model.boiling_technologies[:1]
        # boiling_technologies = [
        #     delistify(boiling_model.boiling_technologies, single=True)
        # ]
    assert (
        len(boiling_technologies) == 1
    ), f"Число варок для sku с данным заквасочником неверное: {len(boiling_technologies)}"
    bt = delistify(boiling_technologies)

    with make("boiling_process"):
        make("pouring", size=(bt.pouring_time // 5, 0))
        make("heating", size=(bt.heating_time // 5, 0))
        make("waiting", size=[0, 0])
        make("adding_lactic_acid", size=(bt.adding_lactic_acid_time // 5, 0))
        make("pumping_off", size=(bt.pumping_off_time // 5, 0))

    packing_process_start = (
        maker.root["boiling_process"].y[0]
        if not is_cream
        else maker.root["boiling_process"]["pumping_off"].x[0] + 2
    )
    with make("packing_process", x=(packing_process_start, 0), push_func=add_push):
        if is_cream:
            make("N", size=(0, 0))
        else:
            make("N", size=(2, 0))
        make("ingredient", size=(bt.ingredient_time // 5, 0))
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
        packing_time = int(custom_round(packing_time, 5, "ceil", pre_round_precision=1))

        make(
            "packing",
            x=(packing_start, 0),
            size=(packing_time // 5, 0),
            push_func=add_push,
        )
    return maker.root


def make_mascarpone_boiling_group(boiling_group_dfs):
    assert len(boiling_group_dfs) in [
        1,
        2,
    ], "Only one or two mascarpone boilings can be put into the group"
    boiling_models = list(
        set(
            [
                boiling_group_df.iloc[0]["boiling"]
                for boiling_group_df in boiling_group_dfs
            ]
        )
    )
    assert len(boiling_models) == 1
    boiling_model = boiling_models[0]

    validator = ClassValidator(window=3)

    def validate(b1, b2):
        validate_disjoint_by_axis(
            b1["packing_process"]["packing"], b2["packing_process"]["packing"]
        )
        # just in case, not needed in reality
        validate_disjoint_by_axis(
            b1["boiling_process"]["pumping_off"], b2["boiling_process"]["pumping_off"]
        )
        assert (
            b2["boiling_process"]["pouring"].x[0]
            >= b1["boiling_process"]["pouring"].y[0]
        )

        # make separation not before pumping_out
        assert (
            b1["packing_process"]["P"].x[0] <= b2["boiling_process"]["pumping_off"].x[0]
        )

    validator.add("boiling", "boiling", validate)

    maker, make = init_block_maker(
        "mascarpone_boiling_group",
        boiling_model=boiling_model,
        boiling_group_dfs=boiling_group_dfs,
    )

    mascarpone_boilings = [
        make_mascorpone_boiling(boiling_group_df, n=i)
        for i, boiling_group_df in enumerate(boiling_group_dfs)
    ]

    for mascarpone_boiling in mascarpone_boilings:
        push(
            maker.root,
            mascarpone_boiling,
            push_func=AxisPusher(start_from="last_beg"),
            validator=validator,
        )

    if len(boiling_group_dfs) == 2:
        # fix waiting time
        b1, b2 = mascarpone_boilings
        waiting_size = (
            b2["boiling_process"]["pouring"].x[0]
            - b1["boiling_process"]["pouring"].y[0]
        )

        for b in [b2["boiling_process"]]:
            b.props.update(x=(b.props["x_rel"][0] - waiting_size, 0))
        for key in ["adding_lactic_acid", "pumping_off"]:
            b = b2["boiling_process"][key]
            b.props.update(x=(b.props["x_rel"][0] + waiting_size, 0))
        b2["boiling_process"]["waiting"].props.update(size=(waiting_size, 0))

    return maker.root
