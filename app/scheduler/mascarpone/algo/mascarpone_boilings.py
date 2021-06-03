# fmt: off

from app.imports.runtime import *
from app.models import *

from utils_ak.block_tree import *


def make_mascorpone_boiling(boiling_group_df, **props):
    sku = boiling_group_df.iloc[0]["sku"]
    is_cream = boiling_group_df.iloc[0]["is_cream"]
    if is_cream:
        sourdough = None
    else:
        sourdough = int(boiling_group_df.iloc[0]["sourdough"])
    boiling_id = boiling_group_df.iloc[0]["boiling_id"]

    boiling_models = sku.made_from_boilings
    boiling_model = utils.delistify(boiling_models, single=True)

    m = BlockMaker(
        "boiling",
        boiling_model=boiling_model,
        boiling_id=boiling_id,
        is_cream=is_cream,
        **props,
    )

    def get_boiling_technology_from_boiling_model(boiling_model):
        if not is_cream:
            boiling_technologies = [
                boiling_technology
                for boiling_technology in boiling_model.boiling_technologies
                if cast_model(MascarponeSourdough, sourdough)
                in boiling_technology.sourdoughs
            ]
        else:
            # todo soon: make properly
            boiling_technologies = boiling_model.boiling_technologies[:1]
            # boiling_technologies = [
            #     delistify(boiling_model.boiling_technologies, single=True)
            # ]
        assert (
            len(boiling_technologies) == 1
        ), f"Число варок для sku с данным заквасочником неверное: {len(boiling_technologies)}"
        return utils.delistify(boiling_technologies, single=True)

    bt = get_boiling_technology_from_boiling_model(boiling_model)

    with m.row("boiling_process"):
        m.row("pouring", size=bt.pouring_time // 5)
        m.row("heating", size=bt.heating_time // 5)
        m.row("waiting", size=0)
        m.row("adding_lactic_acid", size=bt.adding_lactic_acid_time // 5)
        m.row("pumping_off", size=bt.pumping_off_time // 5)

    packing_process_start = (
        m.root["boiling_process"].y[0]
        if not is_cream
        else m.root["boiling_process"]["pumping_off"].x[0] + 2
    )
    with m.row("packing_process", push_func=add_push, x=(packing_process_start, 0)):
        if is_cream:
            m.row("N", size=0)
        else:
            m.row("N", size=2)

        start_from = 0

        with m.row("packing_group"):
            for ind, grp in utils.df_to_ordered_tree(
                boiling_group_df, column="boiling_key", recursive=False
            ):
                bt = get_boiling_technology_from_boiling_model(grp.iloc[0]["boiling"])

                m.row("ingredient", push_func=add_push,
                      size=bt.ingredient_time // 5,
                      x=start_from)
                p = m.row("P", size=2).block

                packing_time = sum(
                    [
                        row["kg"] / row["sku"].packing_speed * 60
                        for i, row in grp.iterrows()
                    ]
                )
                packing_time = int(utils.custom_round(packing_time, 5, "ceil"))

                m.row("packing", push_func=add_push,
                      x=p.props.relative_props["x"][0] + 1,
                      size=packing_time // 5)

                start_from = p.props.relative_props["x"][0] + 2
    return m.root


def make_mascarpone_boiling_group(boiling_group_dfs):
    assert len(boiling_group_dfs) in [
        1,
        2,
    ], "Only one or two mascarpone boilings can be put into the group"

    class Validator(ClassValidator):
        def __init__(self):
            super().__init__(window=3)

        @staticmethod
        def validate__boiling__boiling(b1, b2):
            validate_disjoint_by_axis(
                b1["packing_process"]["packing_group"],
                b2["packing_process"]["packing_group"],
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
                b1["packing_process"]["packing_group"]["P", True][-1].x[0]
                <= b2["boiling_process"]["pumping_off"].x[0]
            )

    m = BlockMaker("mascarpone_boiling_group", boiling_group_dfs=boiling_group_dfs)

    mascarpone_boilings = [
        make_mascorpone_boiling(boiling_group_df, n=i)
        for i, boiling_group_df in enumerate(boiling_group_dfs)
    ]

    for mascarpone_boiling in mascarpone_boilings:
        m.row(mascarpone_boiling,
              push_func=AxisPusher(start_from="last_beg"),
              push_kwargs={'validator': Validator()})

    with code('Fix waiting time'):
        if len(boiling_group_dfs) == 2:
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
            b2["boiling_process"]["waiting"].update_size(size=(waiting_size, 0))
    return m.root
