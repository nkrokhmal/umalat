# fmt: off

from app.imports.runtime import *

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.enum import LineName

from app.scheduler.mozzarella.algo.schedule.awaiting_pusher import AwaitingPusher
from utils_ak.block_tree import *

class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=20)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        # extract boiling models
        boiling_model1 = b1.props['boiling_model']
        boiling_model2 = b2.props['boiling_model']


        with code('Basic validations'):
            validate_disjoint_by_axis(b1["pouring"]["first"]["termizator"], b2["pouring"]["first"]["termizator"])
            validate_disjoint_by_axis(b1["pouring"]["second"]["pouring_off"], b2["pouring"]["second"]["pouring_off"])
            validate_disjoint_by_axis(b1["pouring"]["first"]["pumping_out"], b2["pouring"]["second"]["pouring_off"])
            validate_disjoint_by_axis(b1["pouring"]["second"]["pouring_off"], b2["pouring"]["first"]["pumping_out"])

        with code('Order should be strict inside one configuration sheet'):
            if b1.props["sheet"] == b2.props["sheet"]:
                assert b1.x[0] < b2.x[0]

        with code('Process boilings on the same pouring line'):
            if b1["pouring"].props["pouring_line"] == b2["pouring"].props["pouring_line"]:
                # pourings should not intersect
                validate_disjoint_by_axis(b1["pouring"], b2['pouring'])

                # more than that: five minutes should be between boilings
                assert b1["pouring"].y[0] + 1 <= b2["pouring"].x[0]

                # if boilings use same drenator - drenator should not intersect with meltings
                if b1.props["drenator_num"] == b2.props["drenator_num"]:
                    validate_disjoint_by_axis(b1["melting_and_packing"]["melting"]["meltings"], b2["drenator"])

        # define line names (water/salt) that we work on (which corresponds to the pouring line)
        wln1 = LineName.WATER if b1["pouring"].props["pouring_line"] in ["0", "1"] else LineName.SALT
        wln2 = LineName.WATER if b2["pouring"].props["pouring_line"] in ["0", "1"] else LineName.SALT

        if boiling_model1.line.name == boiling_model2.line.name:
            # same lines

            # basic validation
            validate_disjoint_by_axis(b1["melting_and_packing"]["melting"]["meltings"], b2["melting_and_packing"]["melting"]["meltings"])
            for p1, p2 in itertools.product(b1["melting_and_packing"]["collecting", True], b2["melting_and_packing"]["collecting", True]):
                validate_disjoint_by_axis(p1, p2)

            # if water and different boilings - cannot intersect serving with meltings
            if boiling_model1.line.name == LineName.WATER and boiling_model1 != boiling_model2:
                validate_disjoint_by_axis(b1["melting_and_packing"]["melting"]["meltings"], b2["melting_and_packing"]["melting"]["serving"])

            with code('there should be one hour pause between non-"Палочки 15/7" and "Палочки 15/7" form-factors'):
                mp1 = b1["melting_and_packing"]["melting"]["meltings"]["melting_process", True][-1]
                mp2 = b2["melting_and_packing"]["melting"]["meltings"]["melting_process", True][0]

                bff1_name = mp1.props["bff"].name
                bff2_name = mp2.props["bff"].name

                sticks = ["Палочки 15.0г", "Палочки 7.5г"]
                if bff1_name not in sticks and bff2_name in sticks:
                    assert b1["melting_and_packing"]["melting"]["meltings"].y[0] + 12 <= b2["melting_and_packing"]["melting"]["meltings"].x[0]

            with code('Process lactose switch on salt line'):
                if boiling_model1.line.name == LineName.SALT:
                    if boiling_model1.is_lactose and not boiling_model2.is_lactose:
                        assert b1["melting_and_packing"]["melting"]["meltings"].y[0] + 2 <= b2["melting_and_packing"]["melting"]["serving"].x[0]

                    if not boiling_model1.is_lactose and boiling_model2.is_lactose:
                        assert b1["melting_and_packing"]["melting"]["meltings"].y[0] - 2 <= b2["melting_and_packing"]["melting"]["serving"].x[0]

        else:
            # different lines

            if wln1 == wln2:
                # same working lines (means that salt and water on the same working line - due to salt switching to the first pouring_line)

                # basic validations
                validate_disjoint_by_axis(b1["melting_and_packing"]["melting"]["meltings"], b2["melting_and_packing"]["melting"]["meltings"])
                validate_disjoint_by_axis(b1["melting_and_packing"]["melting"]["meltings"], b2["melting_and_packing"]["melting"]["serving"])
                assert b2["melting_and_packing"]["melting"]["meltings"].x[0] - b1["melting_and_packing"]["melting"]["meltings"].y[0] > 6


    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        validate_disjoint_by_axis(boiling["pouring"]["first"]["termizator"], cleaning)


    @staticmethod
    def validate__cleaning__boiling(b1, b2):
        boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        validate_disjoint_by_axis(cleaning, boiling["pouring"]["first"]["termizator"])

    @staticmethod
    def validate__boiling__packing_configuration(b1, b2):
        boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        if boiling.props["boiling_model"].line.name != packing_configuration.props["line_name"]:
            return

        for p1 in boiling.iter(
            cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]
        ):
            validate_disjoint_by_axis(p1, b2)

    @staticmethod
    def validate__packing_configuration__boiling(b1, b2):
        boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        if boiling.props["boiling_model"].line.name != packing_configuration.props["line_name"]:
            return

        for p1 in boiling.iter(
            cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]
        ):
            validate_disjoint_by_axis(b1, p1)


def make_termizator_cleaning_block(cleaning_type, **kwargs):
    cleaning_name = 'Короткая мойка термизатора' if cleaning_type == 'short' else 'Длинная мойка термизатора'
    washer = cast_model(Washer, cleaning_name)
    m = BlockMaker(
        "cleaning",
        size=(washer.time // 5, 0),
        cleaning_type=cleaning_type,
        **kwargs,
    )
    return m.root


def make_schedule_from_boilings(boilings, date=None, cleanings=None, start_times=None):
    date = date or datetime.now()
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    start_times = {k: v if v else None for k, v in start_times.items()}
    cleanings = cleanings or {}  # {boiling_id: cleaning}

    m = BlockMaker("schedule", date=date)
    m.block("master")
    m.block("extra")
    m.block("extra_packings")

    schedule = m.root

    # init lines df
    lines_df = pd.DataFrame(
        index=[LineName.WATER, LineName.SALT],
        columns=["iter_props", "start_time", "boilings_left", "latest_boiling"],
    )

    # init iter_props
    lines_df.at[LineName.WATER, "iter_props"] = [
        {"pouring_line": str(v1), "drenator_num": str(v2)}
        for v1, v2 in itertools.product([0, 1], [0, 1])
    ]
    lines_df.at[LineName.SALT, "iter_props"] = [
        {"pouring_line": str(v1), "drenator_num": str(v2)}
        for v1, v2 in itertools.product([2, 3], [0, 1])
    ]

    # init start times
    for line_name in [LineName.WATER, LineName.SALT]:
        try:
            lines_df.at[line_name, "start_time"] = cast_time(start_times[line_name])
        except:
            raise AssertionError(
                f"Неверно указано время первой подачи на линии {line_name}"
            )

    # make left_df
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

    # check for missing start time
    if lines_df["start_time"].isnull().any():
        missing_lines = lines_df[lines_df["start_time"].isnull()].index
        raise AssertionError(
            f'Укажите время начала подачи на следующих линиях: {", ".join(missing_lines)}'
        )

    # check for empty input
    assert len(left_df) > 0, "На вход не подано ни одной варки. Укажите хотя бы одну варку для составления расписания."

    # init water boilings using multihead
    multihead_water_boilings = [
        row["boiling"]
        for i, row in left_df.iterrows()
        if boiling_has_multihead_packing(row["boiling"])
        and row["boiling"].props["boiling_model"].line.name == LineName.WATER
    ]

    # init last multihead boiling
    if multihead_water_boilings:
        last_multihead_water_boiling = multihead_water_boilings[-1]
    else:
        last_multihead_water_boiling = None

    def add_one_block_from_line(boiling):
        # extract line name
        line_name = boiling.props["boiling_model"].line.name

        # find start_from
        if not lines_df.at[line_name, "latest_boiling"]:
            # init
            if lines_df.at[line_name, "start_time"]:
                # start time present
                start_from = cast_t(lines_df.at[line_name, "start_time"]) - boiling["melting_and_packing"].x[0]
            else:
                # start time not present - start from overall latest boiling from both lines
                latest_boiling = lines_df[~lines_df["latest_boiling"].isnull()].iloc[0]["latest_boiling"]
                start_from = latest_boiling.x[0]
        else:
            # start from latest boiling
            start_from = lines_df.at[line_name, "latest_boiling"].x[0]

        # add configuration if needed
        if lines_df.at[line_name, "latest_boiling"]:
            configuration_blocks = make_configuration_blocks(
                lines_df.at[line_name, "latest_boiling"],
                boiling,
                m,
                line_name,
                between_boilings=True,
            )
            for conf in configuration_blocks:
                conf.props.update(line_name=line_name)
                push(
                    schedule["master"],
                    conf,
                    push_func=AxisPusher(start_from="beg"),
                    validator=Validator(),
                )

        # filter iter_props: no two boilings allowed sequentially on the same pouring line
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

        # push boiling
        push(
            schedule["master"],
            boiling,
            push_func=AxisPusher(start_from=start_from),
            iter_props=iter_props,
            validator=Validator(),
            max_tries=100,
        )

        # fix water a little bit: try to push water before - allowing awaiting in line
        if line_name == LineName.WATER and lines_df.at[LineName.WATER, "latest_boiling"]:
            boiling.parent.remove_child(boiling)
            push(
                schedule["master"],
                boiling,
                push_func=AwaitingPusher(max_awaiting_period=8),
                validator=Validator(),
                max_tries=9,
            )

        # move rubber packing to extras
        for packing in boiling.iter(cls="packing"):
            if not list(
                packing.iter(
                    cls="process",
                    sku=lambda sku: "Терка" in sku.form_factor.name,
                )
            ):
                # rubber not present
                continue

            packing_copy = m.copy(packing, with_props=True)
            packing_copy.props.update(extra_props={"start_from": packing.x[0]})
            packing.parent.remove_child(packing)
            push(schedule["extra"], packing_copy, push_func=add_push)

        # add multihead boiling after all water boilings if multihead was present
        if boiling == last_multihead_water_boiling:
            push(
                schedule["master"],
                m.create_block(
                    "multihead_cleaning",
                    x=(boiling.y[0], 0),
                    size=(cast_t("03:00"), 0),
                ),
                push_func=add_push,
            )
            push(
                schedule["extra"],
                m.create_block(
                    "multihead_cleaning",
                    x=(boiling.y[0], 0),
                    size=(cast_t("03:00"), 0),
                ),
                push_func=add_push,
            )

        # add cleaning after boiling if needed
        cleaning_type = cleanings.get(boiling.props["boiling_id"])
        if cleaning_type:
            start_from = boiling["pouring"]["first"]["termizator"].y[0]
            cleaning = make_termizator_cleaning_block(
                cleaning_type,
                x=(boiling["pouring"]["first"]["termizator"].y[0], 0),
                rule='manual',
            )
            push(
                schedule["master"],
                cleaning,
                push_func=AxisPusher(start_from=start_from),
                validator=Validator(),
            )

        # set latest boiling
        lines_df.at[line_name, "latest_boiling"] = boiling
        return boiling

    while True:
        # add boilings loop

        # check if finished
        if len(left_df) == 0:
            break

        # check if only salt left -> start working on 3 line
        if (left_df["line_name"] == LineName.SALT).all():
            lines_df.at[LineName.SALT, "iter_props"] = [
                {"pouring_line": str(v1), "drenator_num": str(v2)}
                for v1, v2 in itertools.product([2, 3, 1], [0, 1])
            ]

        # get next rows
        next_rows = [grp.iloc[0] for sheet, grp in left_df.groupby("sheet")]

        # get lines left
        lines_left = len(set([row["line_name"] for row in next_rows]))

        # select next row
        if lines_left == 1:
            # one line of sheet left
            next_row = utils.iter_get(next_rows)
        elif lines_left == 2:
            # filter rows with latest boiling (any boiling is already present for line)
            df = lines_df[~lines_df["latest_boiling"].isnull()]

            if len(df) == 0:
                # first boiling is salt
                line_name = LineName.SALT
            else:
                # choose most latest line
                line_name = (
                    max(df["latest_boiling"], key=lambda b: b.x[0])
                    .props["boiling_model"]
                    .line.name
                )
                # reverse
                line_name = LineName.WATER if line_name == LineName.SALT else LineName.SALT

            # select next row -> first for selected line
            next_row = left_df[left_df["line_name"] == line_name].iloc[0]
        else:
            raise Exception("Should not happen")

        # remove newly added row from left rows
        left_df = left_df[left_df["index"] != next_row["index"]]

        # insert boiling
        add_one_block_from_line(next_row["boiling"])

    # push extra packings
    class ExtraValidator(ClassValidator):
        def __init__(self):
            super().__init__(window=10)

        @staticmethod
        def validate__packing__packing(b1, b2):
            return validate_disjoint_by_axis(b1, b2)

        @staticmethod
        def validate__multihead_cleaning__packing(b1, b2):
            multihead_cleaning, packing = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
            for process in packing.iter(cls="process"):
                packer = utils.delistify(process.props['sku'].packers, single=True)
                if packer.name == 'Мультиголова':
                    validate_disjoint_by_axis(multihead_cleaning, process)
                    assert multihead_cleaning.y[0] + 1 <= process.x[0]

    # add multihead to "extra_packings"
    for multihead_cleaning in schedule["extra"].iter(cls="multihead_cleaning"):
        push(
            schedule["extra_packings"], multihead_cleaning, push_func=add_push
        )

    # add packings to "extra_packings"
    for packing in schedule["extra"].iter(cls="packing"):
        push(
            schedule["extra_packings"],
            packing,
            push_func=AxisPusher(
                start_from=int(packing.props["extra_props"]["start_from"])
            ),
            validator=ExtraValidator(),
        )

    with code('Add cleanings if necessary'):
        # extract boilings
        boilings = schedule["master"]["boiling", True]
        boilings = list(sorted(boilings, key=lambda b: b.x[0]))

        for a, b in utils.iter_pairs(boilings):
            rest = b["pouring"]["first"]["termizator"].x[0] - a["pouring"]["first"]["termizator"].y[0]

            # extract current cleanings
            cleanings = list(schedule["master"].iter(cls="cleaning"))

            # calc in_between and previous cleanings
            in_between_cleanings = [c for c in cleanings if a.x[0] <= c.x[0] <= b.x[0]]
            previous_cleanings = [c for c in cleanings if c.x[0] <= a.x[0]]
            if previous_cleanings:
                previous_cleaning = max(previous_cleanings, key=lambda c: c.x[0])
            else:
                previous_cleaning = None

            if not in_between_cleanings:
                # no current in between cleanings -> try to add if needed

                # if rest is more than an hour and less than 80 minutes -> short cleaning
                if 12 <= rest < 18:
                    cleaning = make_termizator_cleaning_block("short", rule='rest_between_60_and_80')
                    cleaning.props.update(x=(a["pouring"]["first"]["termizator"].y[0], 0))
                    push(schedule["master"], cleaning, push_func=add_push)

                # if rest is more than 80 minutes
                if rest >= 18:
                    if previous_cleaning and a.x[0] - previous_cleaning.x[0] < cast_t("04:00"):
                        # if 4 hours ago or earlier was cleaning -> make short
                        cleaning = make_termizator_cleaning_block("short", rule='rest_after_80_4_hours_cleaning')
                    elif a.x[0] - boilings[0].x[0] < cast_t("04:00"):
                        # if less than 4 hours since day start -> make short
                        cleaning = make_termizator_cleaning_block("short", rule='rest_after_80_4_hours_init')
                    else:
                        # otherwise -> make full
                        cleaning = make_termizator_cleaning_block("full", rule='rest_after_80')
                    cleaning.props.update(x=(a["pouring"]["first"]["termizator"].y[0], 0))
                    push(schedule["master"], cleaning, push_func=add_push)

    # add last full cleaning
    last_boiling = list(schedule["master"].iter(cls="boiling"))[-1]
    start_from = last_boiling["pouring"]["first"]["termizator"].y[0] + 1
    cleaning = make_termizator_cleaning_block("full", rule='closing')  # add five extra minutes
    push(
        schedule["master"],
        cleaning,
        push_func=AxisPusher(start_from=start_from),
        validator=Validator(),
    )

    return schedule
