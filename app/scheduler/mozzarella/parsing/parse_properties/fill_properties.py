from app.imports.runtime import *
from app.scheduler.mozzarella import *
from app.scheduler.mozzarella.properties import *
from app.enum import LineName
from app.scheduler.mozzarella.properties.mozzarella_properties import MozzarellaProperties
from app.scheduler.parsing import *
from app.scheduler.parsing_new.parse_time import *

from utils_ak.block_tree import *


def fill_properties(parsed_schedule, df_bp):
    props = MozzarellaProperties()

    # save boiling_model to parsed_schedule blocks
    for block in list(parsed_schedule.iter(cls=lambda cls: cls in ["boiling", "melting", "packing"])):
        # - remove little blocks
        if "boiling_id" not in block.props.all() or not is_int(block.props["boiling_id"]):

            # NOTE: SHOULD NOT HAPPEN IN NEWER FILES SINCE update 2021.10.21 (# update 2021.10.21)
            logger.error("Removing small block", block=block)
            block.detach_from_parent()
            continue

        # - Update block
        boiling_group_df = df_bp[df_bp["boiling_id"] == int(block.props["boiling_id"])]
        block.props.update(
            boiling_group_df=boiling_group_df,
            line_name=boiling_group_df.iloc[0]["boiling"].line.name,
            boiling_model=boiling_group_df.iloc[0]["boiling"],
        )

    # parse boilings
    boilings = parsed_schedule["boilings"]["boiling", True]
    boilings = list(sorted(boilings, key=lambda b: b.x[0]))
    salt_boilings = [b for b in boilings if b.props["line_name"] == LineName.SALT]
    salt_boilings = list(sorted(salt_boilings, key=lambda b: b.x[0]))
    water_boilings = [b for b in boilings if b.props["line_name"] == LineName.WATER]
    water_boilings = list(sorted(water_boilings, key=lambda b: b.x[0]))

    # filling code is mirroring the pickle parser from app/scheduler/mozzarella/properties.py

    props.bar12_present = "1.2" in [sku.form_factor.name for sku in df_bp["sku"]]

    # - 2.7, 3.3, 3.6 tanks

    _boilings = [b for b in boilings if str(b.props["boiling_model"].percent) == "3.3"]
    if _boilings:
        _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
        props.line33_last_termizator_end_times = [
            cast_human_time(b.x[0] + (b.props["group"][0]["y0"] - b.props["group"][0]["x0"])) for b in _tank_boilings
        ]

    _boilings = [b for b in boilings if str(b.props["boiling_model"].percent) == "3.6"]
    if _boilings:
        _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
        props.line36_last_termizator_end_times = [
            cast_human_time(b.x[0] + (b.props["group"][0]["y0"] - b.props["group"][0]["x0"])) for b in _tank_boilings
        ]

    _boilings = [b for b in boilings if str(b.props["boiling_model"].percent) == "2.7"]
    if _boilings:
        _tank_boilings = [b for i, b in enumerate(_boilings) if (i + 1) % 9 == 0 or i == len(_boilings) - 1]
        props.line27_last_termizator_end_times = [
            cast_human_time(b.x[0] + (b.props["group"][0]["y0"] - b.props["group"][0]["x0"])) for b in _tank_boilings
        ]

    # - Multihead

    multihead_packings = list(
        parsed_schedule.iter(
            cls="packing",
            boiling_group_df=lambda df: df["sku"].iloc[0].packers[0].name == "Мультиголова",
        )
    )
    if multihead_packings:
        props.multihead_end_time = cast_human_time(max(packing.y[0] for packing in multihead_packings))

    water_multihead_packings = list(
        parsed_schedule.iter(
            cls="packing",
            boiling_group_df=lambda df: df["sku"].iloc[0].packers[0].name == "Мультиголова"
            and df.iloc[0]["boiling"].line.name == LineName.WATER,
        )
    )
    if water_multihead_packings:
        props.water_multihead_present = True

    # - Cleanings

    props.short_cleaning_times = [
        cast_human_time(cleaning.x[0])
        for cleaning in parsed_schedule.iter(cls="cleaning")
        if "Короткая мойка" in cleaning.props["group"][0]["label"]
    ]
    props.full_cleaning_times = [
        cast_human_time(cleaning.x[0])
        for cleaning in parsed_schedule.iter(cls="cleaning")
        if "Полная мойка" in cleaning.props["group"][0]["label"]
    ]

    # - Meltings

    if salt_boilings:
        props.salt_melting_start_time = cast_human_time(
            parsed_schedule["salt_meltings"]["melting", True][0].props["melting_start"]
        )

    # - Cheesemakers

    values = []
    for b in parsed_schedule["boilings"]["boiling", True]:
        values.append([b.props["line_num"], b.y[0]])

    df1 = pd.DataFrame(values, columns=["pouring_line", "finish"])
    values = df1.groupby("pouring_line").agg(max).to_dict()["finish"]
    values = list(sorted(values.items(), key=lambda kv: kv[0]))  # [('0', 116), ('1', 97), ('2', 149), ('3', 160)]
    values_dict = dict(values)
    props.cheesemaker1_end_time = cast_human_time(values_dict.get("0"))
    props.cheesemaker2_end_time = cast_human_time(values_dict.get("1"))
    props.cheesemaker3_end_time = cast_human_time(values_dict.get("2"))
    props.cheesemaker4_end_time = cast_human_time(values_dict.get("3"))

    # - Melting end

    def _get_melting_end(line_boilings):
        if not line_boilings:
            return None
        line_boilings = list(sorted(line_boilings, key=lambda b: b.x[0]))
        last_boiling_id = line_boilings[-1].props["boiling_id"]
        last_melting = parsed_schedule.find_one(cls="melting", boiling_id=last_boiling_id)
        return last_melting.props["melting_end_with_cooling"]

    props.water_melting_end_time = cast_human_time(_get_melting_end(water_boilings))
    props.salt_melting_end_time = cast_human_time(_get_melting_end(salt_boilings))

    # - Drenators

    # -- Fill drenators info

    for line_num in range(4):
        line_boilings = [b for b in boilings if b.props["line_num"] == str(line_num)]
        line_boilings = list(sorted(line_boilings, key=lambda b: b.x[0]))

        cur_drenator_num = -1
        for b1, b2 in utils.iter_pairs(line_boilings, method="any_prefix"):

            if not b1:
                cur_drenator_num += 1
            else:
                melting = parsed_schedule.find_one(cls="melting", boiling_id=b1.props["boiling_id"])
                if b2.y[0] - 5 < melting.props["melting_end"]:  # todo later: make pouring off properly [@marklidenberg]
                    cur_drenator_num += 1
                else:

                    # use same drenator for the next boiling
                    pass
            b2.props.update(
                drenator_num=cur_drenator_num % 2,
                drenator_end=b2.y[0] + b2.props["boiling_model"].line.chedderization_time // 5 - 5,
            )  # todo later: make pouring off properly [@marklidenberg]

    # -- Fill drenator properties

    # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
    values = []
    for boiling in boilings:
        values.append(
            [
                boiling.props["drenator_end"],
                boiling.props["line_num"],
                boiling.props["drenator_num"],
            ]
        )
    df = pd.DataFrame(values, columns=["drenator_end", "pouring_line", "drenator_num"])
    df["id"] = df["pouring_line"].astype(int) * 2 + df["drenator_num"].astype(int)
    df = df[["id", "drenator_end"]]
    df = df.drop_duplicates(subset="id", keep="last")
    df = df.reset_index(drop=True)
    df["id"] = df["id"].astype(int) + 1

    df = df.sort_values(by="id")

    values = df.values.tolist()
    values_dict = dict(values)
    props.drenator1_end_time = cast_human_time(values_dict.get(1))
    props.drenator2_end_time = cast_human_time(values_dict.get(2))
    props.drenator3_end_time = cast_human_time(values_dict.get(3))
    props.drenator4_end_time = cast_human_time(values_dict.get(4))
    props.drenator5_end_time = cast_human_time(values_dict.get(5))
    props.drenator6_end_time = cast_human_time(values_dict.get(6))
    props.drenator7_end_time = cast_human_time(values_dict.get(7))
    props.drenator8_end_time = cast_human_time(values_dict.get(8))

    return props
