import itertools


from utils_ak.interactive_imports import *

from app.schedule_maker.time import *
from app.schedule_maker.departments.mozarella.algo.packing import *
from app.enum import LineName

from app.schedule_maker.departments.mozarella.algo.schedule.awaiting_pusher import AwaitingPusher
from datetime import datetime

# todo: optimize
# class_validator = ClassValidator(window=10, window_by_classes={'boiling': {'boiling': 4, 'cleaning': 1, 'packing_configuration': 2},
#                                                                'cleaning': {'boiling': 1, 'cleaning': 1},
#                                                                'packing_configuration': {'boiling': 4}})


master_validator = ClassValidator(window=20)


def validate(b1, b2):
    validate_disjoint_by_axis(
        b1["pouring"]["first"]["termizator"],
        b2["pouring"]["first"]["termizator"],
    )
    validate_disjoint_by_axis(
        b1["pouring"]["second"]["pouring_off"],
        b2["pouring"]["second"]["pouring_off"],
    )
    validate_disjoint_by_axis(
        b1["pouring"]["first"]["pumping_out"],
        b2["pouring"]["second"]["pouring_off"],
    )
    validate_disjoint_by_axis(
        b1["pouring"]["second"]["pouring_off"],
        b2["pouring"]["first"]["pumping_out"],
    )

    if b1.props["sheet"] == b2.props["sheet"]:
        assert b1.x[0] < b2.x[0]

    wl1 = (
        LineName.WATER
        if b1["pouring"].props["pouring_line"] in ["0", "1"]
        else LineName.SALT
    )
    wl2 = (
        LineName.WATER
        if b2["pouring"].props["pouring_line"] in ["0", "1"]
        else LineName.SALT
    )

    # cannot make two boilings on same line at the same time
    if b1["pouring"].props["pouring_line"] == b2["pouring"].props["pouring_line"]:
        validate_disjoint_by_axis(b1["pouring"], b2["pouring"])

        # five minutes between boilings
        assert b1["pouring"].y[0] + 1 <= b2["pouring"].x[0]

        # check drenator
        if b1.props["drenator_num"] == b2.props["drenator_num"]:
            validate_disjoint_by_axis(
                b1["melting_and_packing"]["melting"]["meltings"],
                b2["drenator"],
            )

    if b1.props["boiling_model"].line.name == b2.props["boiling_model"].line.name:
        # same line
        validate_disjoint_by_axis(
            b1["melting_and_packing"]["melting"]["meltings"],
            b2["melting_and_packing"]["melting"]["meltings"],
        )

        # if water and different boilings - cannot intersect serving
        if (
            b1.props["boiling_model"].line.name == LineName.WATER
            and b1.props["boiling_model"] != b2.props["boiling_model"]
        ):
            validate_disjoint_by_axis(
                b1["melting_and_packing"]["melting"]["meltings"],
                b2["melting_and_packing"]["melting"]["serving"],
            )

        # there should be one hour pause between non-"Палочки 15/7" and "Палочки 15/7" form-factors
        mp1 = listify(
            b1["melting_and_packing"]["melting"]["meltings"]["melting_process"]
        )[-1]

        mp2 = listify(
            b2["melting_and_packing"]["melting"]["meltings"]["melting_process"]
        )[0]

        bff1_name = mp1.props["bff"].name
        bff2_name = mp2.props["bff"].name

        sticks = ["Палочки 15.0г", "Палочки 7.5г"]
        if bff1_name not in sticks and bff2_name in sticks:
            assert (
                b1["melting_and_packing"]["melting"]["meltings"].y[0] + 12
                <= b2["melting_and_packing"]["melting"]["meltings"].x[0]
            )

        # collectings
        for p1, p2 in itertools.product(
            listify(b1["melting_and_packing"]["collecting"]),
            listify(b2["melting_and_packing"]["collecting"]),
        ):
            # if p1.props['packing_team_id'] != p2.props['packing_team_id']:
            #     continue
            validate_disjoint_by_axis(p1, p2)

        # add 15 minutes for non-lactose for cleaning of melting-space
        if b1.props["boiling_model"].line.name == LineName.SALT:
            if (
                b1.props["boiling_model"].is_lactose
                and not b2.props["boiling_model"].is_lactose
            ):
                assert (
                    b1["melting_and_packing"]["melting"]["meltings"].y[0] + 2
                    <= b2["melting_and_packing"]["melting"]["serving"].x[0]
                )

            if (
                not b1.props["boiling_model"].is_lactose
                and b2.props["boiling_model"].is_lactose
            ):
                assert (
                    b1["melting_and_packing"]["melting"]["meltings"].y[0] - 2
                    <= b2["melting_and_packing"]["melting"]["serving"].x[0]
                )
    elif wl1 == wl2:
        # salt and water on the same working line - due to salt switching to the first pouring_line
        validate_disjoint_by_axis(
            b1["melting_and_packing"]["melting"]["meltings"],
            b2["melting_and_packing"]["melting"]["meltings"],
        )
        validate_disjoint_by_axis(
            b1["melting_and_packing"]["melting"]["meltings"],
            b2["melting_and_packing"]["melting"]["serving"],
        )
        assert (
            b2["melting_and_packing"]["melting"]["meltings"].x[0]
            - b1["melting_and_packing"]["melting"]["meltings"].y[0]
            > 6
        )  # todo: optimize - add straight to validate disjoint


master_validator.add("boiling", "boiling", validate)


def validate(b1, b2):
    boiling, cleaning = list(
        sorted([b1, b2], key=lambda b: b.props["cls"])
    )  # boiling, cleaning
    validate_disjoint_by_axis(boiling["pouring"]["first"]["termizator"], cleaning)


master_validator.add("boiling", "cleaning", validate)


def validate(b1, b2):
    boiling, cleaning = list(
        sorted([b1, b2], key=lambda b: b.props["cls"])
    )  # boiling, cleaning
    validate_disjoint_by_axis(cleaning, boiling["pouring"]["first"]["termizator"])


master_validator.add("cleaning", "boiling", validate)


def validate(b1, b2):
    boiling, packing_configuration = list(
        sorted([b1, b2], key=lambda b: b.props["cls"])
    )  # boiling, packing_configuration
    if (
        boiling.props["boiling_model"].line.name
        != packing_configuration.props["line_name"]
    ):
        return

    for p1 in boiling.iter(
        cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]
    ):
        validate_disjoint_by_axis(p1, b2)


master_validator.add("boiling", "packing_configuration", validate)


def validate(b1, b2):
    boiling, packing_configuration = list(
        sorted([b1, b2], key=lambda b: b.props["cls"])
    )  # boiling, packing_configuration
    if (
        boiling.props["boiling_model"].line.name
        != packing_configuration.props["line_name"]
    ):
        return

    for p1 in boiling.iter(
        cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]
    ):
        validate_disjoint_by_axis(b1, p1)


master_validator.add("packing_configuration", "boiling", validate)


def make_termizator_cleaning_block(cleaning_type, **kwargs):
    cleaning_duration = (
        40 if cleaning_type == "short" else 80
    )  # todo: take from parameters
    maker, make = init_block_maker(
        "cleaning",
        size=(cleaning_duration // 5, 0),
        cleaning_type=cleaning_type,
        **kwargs,
    )
    return maker.root


def make_schedule_from_boilings(boilings, date=None, cleanings=None, start_times=None):
    date = date or datetime.now()
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    start_times = {k: v if v else None for k, v in start_times.items()}
    cleanings = cleanings or {}  # {boiling_id: cleaning}

    maker, make = init_block_maker("schedule", date=date)

    make("master", push_func=add_push)
    make("extra", push_func=add_push)
    make("extra_packings", push_func=add_push)

    schedule = maker.root

    lines_df = pd.DataFrame(
        index=[LineName.WATER, LineName.SALT],
        columns=["iter_props", "start_time", "boilings_left", "latest_boiling"],
    )
    # lines_df.at[LineName.WATER, 'iter_props'] = [{'pouring_line': str(v)} for v in [0, 1]]
    # lines_df.at[LineName.SALT, 'iter_props'] = [{'pouring_line': str(v)} for v in [2, 3]]
    lines_df.at[LineName.WATER, "iter_props"] = [
        {"pouring_line": str(v1), "drenator_num": str(v2)}
        for v1, v2 in itertools.product([0, 1], [0, 1])
    ]
    lines_df.at[LineName.SALT, "iter_props"] = [
        {"pouring_line": str(v1), "drenator_num": str(v2)}
        for v1, v2 in itertools.product([2, 3], [0, 1])
    ]

    for line_name in [LineName.WATER, LineName.SALT]:
        try:
            lines_df.at[line_name, "start_time"] = cast_time(start_times[line_name])
        except:
            raise AssertionError(
                f"Неверно указано время первой подачи на линии {line_name}"
            )

    # make sheets df
    values = [
        [
            boiling,
            boiling.props["boiling_model"].line.name,
            boiling.props["sheet"],
        ]
        for boiling in boilings
    ]
    left_df = (
        pd.DataFrame(values, columns=["boiling", "line_name", "sheet"])
        .reset_index()
        .sort_values(by=["sheet", "index"])
    )

    lines_df["latest_boiling"] = None

    if lines_df["start_time"].isnull().any():
        missing_lines = lines_df[lines_df["start_time"].isnull()].index
        raise AssertionError(
            f'Укажите время начала подачи на следующих линиях: {", ".join(missing_lines)}'
        )

    assert (
        len(left_df) > 0
    ), "На вход не подано ни одной варки. Укажите хотя бы одну варку для составления расписания."

    multihead_water_boilings = [
        row["boiling"]
        for i, row in left_df.iterrows()
        if boiling_has_multihead_packing(row["boiling"])
        and row["boiling"].props["boiling_model"].line.name == LineName.WATER
    ]

    if multihead_water_boilings:
        last_multihead_water_boiling = multihead_water_boilings[-1]
    else:
        last_multihead_water_boiling = None

    def add_one_block_from_line(boiling):
        line_name = boiling.props["boiling_model"].line.name
        if not lines_df.at[line_name, "latest_boiling"]:
            if lines_df.at[line_name, "start_time"]:
                start_from = (
                    cast_t(lines_df.at[line_name, "start_time"])
                    - boiling["melting_and_packing"].x[0]
                )
            else:
                latest_boiling = lines_df[~lines_df["latest_boiling"].isnull()].iloc[0][
                    "latest_boiling"
                ]
                start_from = latest_boiling.x[0]
        else:
            start_from = lines_df.at[line_name, "latest_boiling"].x[0]

        # add configuration if needed
        if lines_df.at[line_name, "latest_boiling"]:
            configuration_blocks = make_configuration_blocks(
                lines_df.at[line_name, "latest_boiling"],
                boiling,
                maker,
                line_name,
                between_boilings=True,
            )
            for conf in configuration_blocks:
                conf.props.update(line_name=line_name)
                push(
                    schedule["master"],
                    conf,
                    push_func=AxisPusher(start_from="beg"),
                    validator=master_validator,
                )

        # no two boilings allowed sequentially on the same pouring line
        iter_props = lines_df.at[line_name, "iter_props"]
        if lines_df.at[line_name, "latest_boiling"]:
            current_pouring_line = lines_df.at[line_name, "latest_boiling"].props[
                "pouring_line"
            ]
            iter_props = [
                props
                for props in iter_props
                if props["pouring_line"] != current_pouring_line
            ]

        push(
            schedule["master"],
            boiling,
            push_func=AxisPusher(start_from=start_from),
            iter_props=iter_props,
            validator=master_validator,
            max_tries=100,
        )

        # try to push water before - allowing awaiting in line
        # remove boiling from parent for now
        if (
            line_name == LineName.WATER
            and lines_df.at[LineName.WATER, "latest_boiling"]
        ):
            boiling.disconnect()
            push(
                schedule["master"],
                boiling,
                push_func=AwaitingPusher(max_awaiting_period=8),
                validator=master_validator,
                max_tries=9,
            )

        # take rubber packing to extras
        for packing in boiling.iter(cls="packing"):
            if not list(
                packing.iter(
                    cls="process",
                    sku=lambda sku: "Терка" in sku.form_factor.name,
                )
            ):
                continue
            packing_copy = maker.copy(packing, with_props=True)
            packing_copy.props.update(extra_props={"start_from": packing.x[0]})
            packing.disconnect()
            push(schedule["extra"], packing_copy, push_func=add_push)

        # todo: put to the place of last multihead usage!
        # add multihead boiling after all water boilings if multihead was present
        if boiling == last_multihead_water_boiling:
            push(
                schedule["master"],
                maker.create_block(
                    "multihead_cleaning",
                    x=(boiling.y[0], 0),
                    size=(cast_t("03:00"), 0),
                ),
                push_func=add_push,
            )
            push(
                schedule["extra"],
                maker.create_block(
                    "multihead_cleaning",
                    x=(boiling.y[0], 0),
                    size=(cast_t("03:00"), 0),
                ),
                push_func=add_push,
            )

        cleaning_type = cleanings.get(boiling.props["boiling_id"])
        if cleaning_type:
            start_from = boiling["pouring"]["first"]["termizator"].y[0]
            text = (
                "Полная мойка" if cleaning_type == "full" else "Короткая мойка"
            )  # todo: refactor
            cleaning = make_termizator_cleaning_block(
                cleaning_type,
                x=(boiling["pouring"]["first"]["termizator"].y[0], 0),
                text=text,
            )
            push(
                schedule["master"],
                cleaning,
                push_func=AxisPusher(start_from=start_from),
                validator=master_validator,
            )

        lines_df.at[line_name, "latest_boiling"] = boiling
        return boiling

    while True:
        if len(left_df) == 0:
            # finished
            break

        if (left_df["line_name"] == LineName.SALT).all():
            # only salt left
            # start working on 3 line for salt
            # lines_df.at[LineName.SALT, 'iter_props'] = [{'pouring_line': str(v)} for v in [2, 3, 1]]
            lines_df.at[LineName.SALT, "iter_props"] = [
                {"pouring_line": str(v1), "drenator_num": str(v2)}
                for v1, v2 in itertools.product([2, 3, 1], [0, 1])
            ]

        # get next boiling_rows for
        next_rows = [grp.iloc[0] for sheet, grp in left_df.groupby("sheet")]

        lines_left = len(set([row["line_name"] for row in next_rows]))
        if lines_left == 1:
            # one line of sheet left
            next_row = iter_get(next_rows)
        elif lines_left == 2:
            df = lines_df[~lines_df["latest_boiling"].isnull()]
            if len(df) == 0:
                # begin with salt
                line_name = LineName.SALT
            else:
                line_name = (
                    max(df["latest_boiling"], key=lambda b: b.x[0])
                    .props["boiling_model"]
                    .line.name
                )
                # reverse
                line_name = (
                    LineName.WATER if line_name == LineName.SALT else LineName.SALT
                )
            next_row = left_df[left_df["line_name"] == line_name].iloc[0]
        else:
            raise Exception("Should not happen")
        left_df = left_df[left_df["index"] != next_row["index"]]
        add_one_block_from_line(next_row["boiling"])

    # push extra packings
    extra_packings_validator = ClassValidator(window=10)
    extra_packings_validator.add("packing", "packing", validate_disjoint_by_axis)

    def validate(b1, b2):
        multihead_cleaning, packing = list(
            sorted([b1, b2], key=lambda b: b.props["cls"])
        )  # boiling, cleaning
        for process in packing.iter(cls="process"):
            # todo: switch
            # if process.props['sku'].packer.name == 'Мультиголова'
            if (
                process.props["sku"].name
                == 'Сулугуни "Умалат" (для хачапури), 45%, 0,12 кг, ф/п'
            ):
                validate_disjoint_by_axis(multihead_cleaning, process)
                assert multihead_cleaning.y[0] + 1 <= process.x[0]

    logger.debug("Extra", block=schedule["extra"])
    extra_packings_validator.add("multihead_cleaning", "packing", validate)

    for multihead_cleaning in schedule["extra"].iter(cls="multihead_cleaning"):
        push(schedule["extra_packings"], multihead_cleaning, push_func=add_push)

    for packing in schedule["extra"].iter(cls="packing"):
        push(
            schedule["extra_packings"],
            packing,
            push_func=AxisPusher(
                start_from=int(packing.props["extra_props"]["start_from"])
            ),
            validator=extra_packings_validator,
        )

    # add cleanings if necessary
    boilings = listify(schedule["master"]["boiling"])
    boilings = list(sorted(boilings, key=lambda b: b.x[0]))

    for a, b in SimpleIterator(boilings).iter_sequences(2):
        rest = (
            b["pouring"]["first"]["termizator"].x[0]
            - a["pouring"]["first"]["termizator"].y[0]
        )

        cleanings = list(schedule["master"].iter(cls="cleaning"))

        in_between_cleanings = [c for c in cleanings if a.x[0] <= c.x[0] <= b.x[0]]
        previous_cleanings = [c for c in cleanings if c.x[0] <= a.x[0]]
        if previous_cleanings:
            previous_cleaning = max(previous_cleanings, key=lambda c: c.x[0])
        else:
            previous_cleaning = None

        if not in_between_cleanings:
            if 12 <= rest < 18:
                cleaning = make_termizator_cleaning_block(
                    "short", text="Короткая мойка"
                )
                cleaning.props.update(x=(a["pouring"]["first"]["termizator"].y[0], 0))
                push(schedule["master"], cleaning, push_func=add_push)

            if rest >= 18:
                if previous_cleaning and (a.x[0] - previous_cleaning.x[0]) < cast_t(
                    "04:00"
                ):
                    cleaning = make_termizator_cleaning_block(
                        "short", text="Короткая мойка"
                    )  # 4 часа
                elif (a.x[0] - boilings[0].x[0]) < cast_t("04:00"):
                    cleaning = make_termizator_cleaning_block(
                        "short", text="Короткая мойка"
                    )  # 4 часа
                else:
                    cleaning = make_termizator_cleaning_block(
                        "full", text="Полная мойка"
                    )
                cleaning.props.update(x=(a["pouring"]["first"]["termizator"].y[0], 0))
                push(schedule["master"], cleaning, push_func=add_push)

    last_boiling = list(schedule["master"].iter(cls="boiling"))[-1]
    start_from = last_boiling["pouring"]["first"]["termizator"].y[0] + 1
    cleaning = make_termizator_cleaning_block(
        "full", text="Полная мойка"
    )  # add five extra minutes
    push(
        schedule["master"],
        cleaning,
        push_func=AxisPusher(start_from=start_from),
        validator=master_validator,
    )

    return schedule