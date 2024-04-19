import re

from datetime import datetime
from typing import Union

import pandas as pd

from loguru import logger
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import delistify
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.iteration.simple_iterator import iter_pairs
from utils_ak.numeric.types import is_int, is_int_like
from utils_ak.portion.portion_tools import calc_interval_length, cast_interval

from app.enum import LineName
from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.mozzarella.properties.mozzarella_properties import MozzarellaProperties
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan
from app.scheduler.parsing_new_utils.parse_time_utils import cast_time_from_hour_label
from app.scheduler.parsing_utils.load_cells_df import load_cells_df
from app.scheduler.parsing_utils.parse_block import parse_elements
from app.scheduler.time_utils import cast_human_time, cast_t


def _is_datetime(v: Union[str, datetime]):
    # main check 09.07.2023 format, but other formats are also possible

    if isinstance(v, datetime):
        return True

    from dateutil.parser import parse

    if len(v) < 8:
        # skip 00, 05, 10,
        return False
    try:
        parse(v)
        return True
    except:
        return False


def _filter_func(group):
    try:
        return is_int_like(group[0]["label"].split(" ")[0])
    except:
        return False


def _split_func(row):
    try:
        return is_int_like(row["label"].split(" ")[0])
    except:
        return False


def parse_schedule_file(wb_obj):
    cells_df = load_cells_df(wb_obj, "Расписание")

    m = BlockMaker("root")

    # - Find start times

    time_index_row_nums = cells_df[cells_df["label"].astype(str).apply(_is_datetime)]["x1"].unique()

    start_times = []

    for row_num in time_index_row_nums:
        start_times.append(
            cast_time_from_hour_label(cells_df[(cells_df["x0"] == 5) & (cells_df["x1"] == row_num)].iloc[0]["label"])
        )

    start_times = [cast_t(v) for v in start_times]

    # - Precaution for minimum start time

    minimum_start_time = "21:00"
    start_times = [t if t <= cast_t(minimum_start_time) else t - 24 * 12 for t in start_times]

    # - Calc split rows

    cells_df1 = cells_df[cells_df["x0"] >= 5]  # column header out

    cheese_maker_headers = []
    water_melting_headers = []
    salt_melting_headers = []
    headers = []

    for row_num in cells_df1["x1"].unique():
        row_labels = [str(row["label"]) for i, row in cells_df1[cells_df1["x1"] == row_num].iterrows()]
        row_labels = [re.sub(r"\s+", " ", label) for label in row_labels if label]

        if {"налив/внесение закваски", "схватка"}.issubset(set(row_labels)):
            cheese_maker_headers.append(row_num - 1)

        if "подача и вымешивание" in row_labels and "посолка" not in row_labels:
            water_melting_headers.append(row_num + 1)

        if {"подача и вымешивание", "посолка", "плавление/формирование"}.issubset(set(row_labels)):
            salt_melting_headers.append(row_num - 1)

        # -- Find all headers

        _labels = [label.replace("налив", "") for label in row_labels]
        _labels = [re.sub(r"\s+", "", label) for label in _labels]
        int_labels = [int(label) for label in _labels if is_int_like(label)]

        if not ("05" in row_labels and "55" in row_labels):
            # not a time header
            if int_labels:
                headers.append(row_num)

    cheese_maker_headers = [0] * (4 - len(cheese_maker_headers)) + cheese_maker_headers

    packing_headers = set(headers) - set(cheese_maker_headers) - set(water_melting_headers) - set(salt_melting_headers)
    packing_headers = list(sorted(packing_headers))
    if water_melting_headers and salt_melting_headers:
        packing_headers = packing_headers[:2]
    else:
        # no water or no salt
        packing_headers = packing_headers[:1]

    cheese_maker_headers = list(sorted(cheese_maker_headers))
    water_melting_headers = list(sorted(water_melting_headers))
    salt_melting_headers = list(sorted(salt_melting_headers))
    packing_headers = list(sorted(packing_headers))

    # - Parse blocks

    parse_elements(
        m=m,
        cells_df=cells_df,
        label="boilings",
        element_label="boiling",
        rows=cheese_maker_headers,
        start_time=start_times[0],
        filter_=_filter_func,
        split_func=_split_func,
    )

    parse_elements(m, cells_df, "cleanings", "cleaning", [cheese_maker_headers[-1] - 8], start_times[0])

    # -- Parse water melting

    if water_melting_headers:
        parse_elements(
            m=m,
            cells_df=cells_df,
            label="water_meltings",
            element_label="melting",
            rows=water_melting_headers,
            start_time=start_times[1],
            filter_=_filter_func,
            split_func=_split_func,
        )

        # todo maybe: make properly [@marklidenberg]

        # - Meta info to water meltings

        # -- Melting end

        for melting in m.root["water_meltings"].children:
            melting.props.update(melting_end=melting.y[0])

        # -- Melting end with cooling

        df_formings = cells_df[cells_df["label"] == "охлаждение"]

        # fix start times and column header
        df_formings["x0"] += start_times[1] - 5
        df_formings["y0"] += start_times[1] - 5
        df_formings["x1"] += start_times[1] - 5
        df_formings["y1"] += start_times[1] - 5

        df_formings = df_formings.sort_values(by="x0")
        for i, row in df_formings.iterrows():
            overlapping = [
                m
                for m in m.root["water_meltings"].children
                if calc_interval_length(cast_interval(m.x[0], m.y[0]) & cast_interval(row["x0"], row["y0"])) > 0
            ]
            if not overlapping:
                # first cooling in each boiling does not qualify the filter
                continue

            # todo later: on the way, make properly [@marklidenberg]
            # choose melting with maxixum coverage
            melting = max(
                overlapping,
                key=lambda m: calc_interval_length(cast_interval(m.x[0], m.y[0]) & cast_interval(row["x0"], row["y0"]))
                / calc_interval_length(cast_interval(m.x[0], m.y[0])),
            )

            # melting = delistify(overlapping, single=True)
            cooling_length = row["y0"] - melting.x[0]
            melting.props.update(melting_end_with_cooling=melting.y[0] + cooling_length)

        parse_elements(
            m=m,
            cells_df=cells_df,
            label="water_packings",
            element_label="packing",
            rows=packing_headers[:1],
            start_time=start_times[1],
            split_func=_split_func,
            filter_=_filter_func,
        )

    # -- Parse salt melting

    if salt_melting_headers:
        parse_elements(
            m=m,
            cells_df=cells_df,
            label="salt_meltings",
            element_label="melting",
            rows=salt_melting_headers,
            start_time=start_times[1],
            split_func=_split_func,
            filter_=_filter_func,
        )

        # todo maybe: make properly [@marklidenberg]

        # - Add salt forming info to meltings

        df_formings = cells_df[
            (cells_df["label"] == "плавление/формирование") & (cells_df["x1"] >= salt_melting_headers[0])
        ]
        df_formings["serving_start"] = df_formings["x0"].apply(
            lambda x0: cells_df[(cells_df["y0"] == x0) & (cells_df["label"] == "подача и вымешивание")].iloc[0]["x0"]
        )

        # fix start times and column header
        df_formings["x0"] = df_formings["x0"] + start_times[1] - 5
        df_formings["y0"] = df_formings["y0"] + start_times[1] - 5
        df_formings["x1"] = df_formings["x1"] + start_times[1] - 5
        df_formings["y1"] = df_formings["y1"] + start_times[1] - 5
        df_formings["serving_start"] = df_formings["serving_start"] + start_times[1] - 5

        df_formings = df_formings.sort_values(by="x0")
        for i, row in df_formings.iterrows():
            melting = delistify(
                [m for m in m.root["salt_meltings"].children if m.x[0] == row["serving_start"]], single=True
            )
            melting.props.update(melting_start=row["x0"], melting_end=row["y0"], melting_end_with_cooling=melting.y[0])

        # - Add salt packing info to meltings

        parse_elements(
            m=m,
            cells_df=cells_df,
            label="salt_packings",
            element_label="packing",
            rows=[packing_headers[-1], packing_headers[-1] + 6],
            start_time=start_times[1],
            split_func=_split_func,
            filter_=_filter_func,
        )

    return m.root


def prepare_boiling_plan(parsed_schedule, boiling_plan_df):
    boiling_plan_df["line_name"] = boiling_plan_df["line"].apply(lambda line: line.name)
    for line_name, grp_line in boiling_plan_df.groupby("line_name"):
        if line_name == LineName.WATER:
            boiling_ids = [b.props["label"] for b in parsed_schedule["water_packings"].children]
        else:
            boiling_ids = [b.props["label"] for b in parsed_schedule["salt_packings"].children]

        boiling_ids = list(sorted(set(boiling_ids)))

        if len(boiling_ids) != len(grp_line["group_id"].unique()):
            raise Exception(
                f'Wrong number of boiling ids: {len(boiling_ids)}, should be: {len(grp_line["group_id"].unique())}'
            )

        for i, (_, grp) in enumerate(grp_line.groupby("group_id")):
            boiling_plan_df.loc[grp.index, "boiling_id"] = boiling_ids[i]
    boiling_plan_df["boiling_id"] = boiling_plan_df["boiling_id"].astype(int)
    return boiling_plan_df


def fill_properties(parsed_schedule, boiling_plan_df):
    props = MozzarellaProperties()

    # save boiling_model to parsed_schedule blocks
    for block in list(parsed_schedule.iter(cls=lambda cls: cls in ["boiling", "melting", "packing"])):
        # remove little blocks
        if "boiling_id" not in block.props.all() or not is_int(block.props["boiling_id"]):
            # NOTE: SHOULD NOT HAPPEN IN NEWER FILES SINCE update 2021.10.21 (# update 2021.10.21)
            logger.error("Removing small block", block=block)
            block.detach_from_parent()
            continue
        boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == int(block.props["boiling_id"])]
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

    props.bar12_present = "1.2" in [sku.form_factor.name for sku in boiling_plan_df["sku"]]

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
        for b1, b2 in iter_pairs(line_boilings, method="any_prefix"):
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


def parse_properties(filename):
    parsed_schedule = parse_schedule_file(filename)
    boiling_plan_df = to_boiling_plan(filename)
    boiling_plan_df = prepare_boiling_plan(parsed_schedule, boiling_plan_df=boiling_plan_df)
    props = fill_properties(parsed_schedule, boiling_plan_df=boiling_plan_df)
    return props


def test():
    import warnings

    warnings.filterwarnings("ignore")
    from lessmore.utils.easy_printing.print_json import print_json

    print_json(
        dict(
            parse_properties(
                """/Users/marklidenberg/Documents/coding/repos/umalat/app/scheduler/mozzarella/draw_frontend/schedule3.xlsx"""
            )
        )
    )


if __name__ == "__main__":
    test()
