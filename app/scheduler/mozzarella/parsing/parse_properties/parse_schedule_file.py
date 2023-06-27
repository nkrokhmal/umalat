from app.imports.runtime import *
from app.scheduler.mozzarella import *
from app.scheduler.mozzarella.properties import *
from app.scheduler.parsing import *
from app.scheduler.parsing_new.parse_time import *

from utils_ak.block_tree import *


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

    # - Load cells dataframe

    df = load_cells_df(wb_obj, "Расписание")

    # - Init block maker

    m = BlockMaker("root")

    # - Find start times

    time_index_row_nums = df[df["label"].astype(str).str.contains("График")]["x1"].unique()

    start_times = []

    for row_num in time_index_row_nums:
        start_times.append(cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row_num)].iloc[0]["label"]))

    start_times = [cast_t(v) for v in start_times]

    # - Precaution for minimum start time

    minimum_start_time = "21:00"
    start_times = [t if t <= cast_t(minimum_start_time) else t - 24 * 12 for t in start_times]

    # - Calc split rows and find headers

    df1 = df[df["x0"] >= 5]  # column header out

    cheese_maker_headers = []
    water_melting_headers = []
    salt_melting_headers = []
    headers = []

    for row_num in df1["x1"].unique():

        # - Find some headers

        row_labels = [str(row["label"]) for i, row in df1[df1["x1"] == row_num].iterrows()]
        row_labels = [re.sub(r"\s+", " ", label) for label in row_labels if label]

        if {"налив/внесение закваски", "схватка"}.issubset(set(row_labels)):
            cheese_maker_headers.append(row_num - 1)

        if "подача и вымешивание" in row_labels and "посолка" not in row_labels:
            water_melting_headers.append(row_num + 1)

        if {"подача и вымешивание", "посолка", "плавление/формирование"}.issubset(set(row_labels)):
            salt_melting_headers.append(row_num - 1)

        # - Find all headers

        _labels = [label.replace("налив", "") for label in row_labels]
        _labels = [re.sub(r"\s+", "", label) for label in _labels]
        int_labels = [int(label) for label in _labels if utils.is_int_like(label)]

        if not ("05" in row_labels and "55" in row_labels):

            # not a time header
            if int_labels:
                headers.append(row_num)

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

    parse_block(
        m,
        df,
        "boilings",
        "boiling",
        cheese_maker_headers,
        start_times[0],
        filter=_filter_func,
        split_func=_split_func,
    )

    parse_block(m, df, "cleanings", "cleaning", [cheese_maker_headers[-1] - 8], start_times[0])

    if water_melting_headers:
        parse_block(
            m,
            df,
            "water_meltings",
            "melting",
            water_melting_headers,
            start_times[1],
            filter=_filter_func,
            split_func=_split_func,
        )

        # todo maybe: make properly [@marklidenberg]
        with code("meta info to water meltings"):
            with code("melting_end"):
                for melting in m.root["water_meltings"].children:
                    melting.props.update(melting_end=melting.y[0])

            with code("melting_end_with_cooling"):
                df_formings = df[df["label"] == "охлаждение"]

                with code("fix start times and column header"):
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
                        key=lambda m: calc_interval_length(
                            cast_interval(m.x[0], m.y[0]) & cast_interval(row["x0"], row["y0"])
                        )
                        / calc_interval_length(cast_interval(m.x[0], m.y[0])),
                    )

                    # melting = utils.delistify(overlapping, single=True)
                    cooling_length = row["y0"] - melting.x[0]
                    melting.props.update(melting_end_with_cooling=melting.y[0] + cooling_length)
        parse_block(
            m,
            df,
            "water_packings",
            "packing",
            packing_headers[:1],
            start_times[1],
            split_func=_split_func,
            filter=_filter_func,
        )

    if salt_melting_headers:
        parse_block(
            m,
            df,
            "salt_meltings",
            "melting",
            salt_melting_headers,
            start_times[1],
            split_func=_split_func,
            filter=_filter_func,
        )

        # - Add salt forming info to meltings

        df_formings = df[(df["label"] == "плавление/формирование") & (df["x1"] >= salt_melting_headers[0])]

        df_formings["serving_start"] = df_formings["x0"].apply(
            lambda x0: df[(df["y0"] == x0) & (df["label"] == "подача и вымешивание")].iloc[0]["x0"]
        )

        with code("fix start times and column header"):
            df_formings["x0"] += start_times[1] - 5
            df_formings["y0"] += start_times[1] - 5
            df_formings["x1"] += start_times[1] - 5
            df_formings["y1"] += start_times[1] - 5
            df_formings["serving_start"] += start_times[1] - 5

        df_formings = df_formings.sort_values(by="x0")
        for i, row in df_formings.iterrows():
            melting = utils.delistify(
                [m for m in m.root["salt_meltings"].children if m.x[0] == row["serving_start"]], single=True
            )
            melting.props.update(melting_start=row["x0"], melting_end=row["y0"], melting_end_with_cooling=melting.y[0])

        # - Parse block

        parse_block(
            m,
            df,
            "salt_packings",
            "packing",
            [packing_headers[-1], packing_headers[-1] + 6],
            start_times[1],
            split_func=_split_func,
            filter=_filter_func,
        )

    # - Return block

    return m.root
