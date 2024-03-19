import types

import pandas as pd

from loguru import logger
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher, ShiftPusher
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.numeric import custom_round
from utils_ak.optimizer.optimizer import optimize

from app.scheduler.time_utils import cast_t


# todo maybe: put in more proper place
def calc_scotta_input_tanks(ricotta_n_boilings, adygea_n_boilings, milk_project_n_boilings):
    total_scotta = (
        (1900 - 130) * ricotta_n_boilings + adygea_n_boilings * 370 + milk_project_n_boilings * 2400
    )  # todo maybe: take from parameters

    assert (
        total_scotta < 80000 + 60000 + 60000
    ), "Скотты больше, чем могут вместить танки. "  # todo maybe: take from parameters

    left_scotta = total_scotta
    values = [["4", 0.0], ["5", 0.0], ["8", 0.0]]
    for value in values:
        cur_scotta = min(80000, left_scotta)
        value[1] = cur_scotta / 1000.0  # value in ton
        left_scotta -= cur_scotta
    return values


class CleaningValidator(ClassValidator):
    def __init__(self, window=30, ordered=True):
        self.ordered = ordered
        super().__init__(window=window)

    def validate__cleaning__cleaning(self, b1, b2):
        validate_disjoint_by_axis(b1, b2, distance=2, ordered=self.ordered)


def run_order(function_or_generators, order):
    for i in order:
        obj = function_or_generators[i]
        if callable(obj):
            obj()
        elif isinstance(obj, types.GeneratorType):
            next(obj)


def _make_contour_1(properties_by_department: dict, basement_brine: bool = False):
    # - Init block maker

    m = BlockMaker("1 contour")

    # - Линия подвал рассол

    if basement_brine:
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t("07:00"), validator=CleaningValidator(ordered=False)),
            size=cast_t("00:55"),
            label="Линия подвал рассол",
        )

    # - Линия отгрузки сырья

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("00:00"), validator=CleaningValidator(ordered=False)),
        size=cast_t("00:55"),
        label="Линия отгрузки сырья",
    )

    # - Танки сырого молока

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("11:00"), validator=CleaningValidator(ordered=False)),
        size=cast_t("01:20"),
        label="Танк сырого молока 1",
    )
    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("17:00"), validator=CleaningValidator(ordered=False)),
        size=cast_t("01:20"),
        label="Танк сырого молока 2",
    )
    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("22:00"), validator=CleaningValidator(ordered=False)),
        size=cast_t("01:20"),
        label="Танк сырого молока 3",
    )

    # - Линия приемки молока

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("03:00"), validator=CleaningValidator(ordered=False)),
        size=cast_t("00:55"),
        label="Линия приемки молока 1",
    )
    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("04:00"), validator=CleaningValidator(ordered=False)),
        size=cast_t("00:55"),
        label="Линия приемки молока 2",
    )

    return m.root


def make_contour_1(properties, *args, **kwargs):
    df = optimize(_make_contour_1, lambda b: -b.y[0], properties, *args, **kwargs)
    return df.iloc[-1]["output"]


def make_contour_2(properties):
    m = BlockMaker("2 contour")
    m.row("cleaning", push_func=add_push, size=cast_t("01:20"), x=cast_t("12:00"), label="Линия обрата в сливки")

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:20"),
        label="Сливки от пастера 25",
    )

    with code("Мультиголова"):
        if properties["mozzarella"].multihead_end_time:
            multihead_end = cast_t(properties["mozzarella"].multihead_end_time) + 12
            m.row(
                "cleaning",
                push_func=AxisPusher(start_from=["max_end", multihead_end], validator=CleaningValidator()),
                size=cast_t("01:20"),
                label="Комет",
            )

        if properties["mozzarella"].water_multihead_present:
            m.row(
                "cleaning",
                push_func=AxisPusher(validator=CleaningValidator()),
                size=cast_t("01:20"),
                label="Фасовочная вода",
            )

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("1:04:00"), validator=CleaningValidator()),
        size=cast_t("01:20"),
        label="Танк ЖВиКС 1",
    )

    m.row("cleaning", push_func=AxisPusher(validator=CleaningValidator()), size=cast_t("01:20"), label="Танк ЖВиКС 2")

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:20"),
        label="Жирная вода на сепаратор",
    )

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:20"),
        label="Сливки от сепаратора жирной воды",
    )

    return m.root


def _make_contour_3(
    properties,
    order1=(0, 1, 1, 1, 1),
    order2=(0, 0, 0, 0, 0, 1),
    molder=False,
    alternative=False,
    is_tomorrow_day_off=False,
):
    m = BlockMaker("3 contour")

    for cleaning_time in properties["mozzarella"].short_cleaning_times:
        m.row(
            "cleaning",
            push_func=add_push,
            size=cast_t("00:40"),
            x=cast_t(cleaning_time),
            label="Короткая мойка термизатора",
        )

    for cleaning_time in properties["mozzarella"].full_cleaning_times:
        m.row(
            "cleaning",
            push_func=add_push,
            size=cast_t("01:20"),
            x=cast_t(cleaning_time),
            label="Полная мойка термизатора",
        )

    def f1():
        if properties["mozzarella"].salt_melting_start_time:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    validator=CleaningValidator(ordered=False),
                    start_from=cast_t(properties["mozzarella"].salt_melting_start_time) + 6,
                ),
                size=90 // 5,
                label="Контур циркуляции рассола",
            )

    def g2():
        with code("cheese_makers"):
            # get when cheese makers end (values -> [('1', 97), ('0', 116), ('2', 149), ('3', 160)])
            values = properties["mozzarella"].cheesemaker_times()

            # convert time to t
            for value in values:
                value[0] = str(value[0])
                value[1] = cast_t(value[1])
            values = list(sorted(values, key=lambda value: value[1]))

            for n, cheese_maker_end in values:
                m.row(
                    "cleaning",
                    push_func=AxisPusher(start_from=cheese_maker_end, validator=CleaningValidator(ordered=False)),
                    size=cast_t("01:20"),
                    label=f"Сыроизготовитель {int(n)}",
                )
                yield

            used_ids = set([value[0] for value in values])

        with code("non-used cheesemakers"):
            non_used_ids = set([str(x) for x in range(1, 5)]) - used_ids
            for id in non_used_ids:
                m.row(
                    "cleaning",
                    push_func=AxisPusher(start_from=cast_t("10:00"), validator=CleaningValidator(ordered=False)),
                    size=cast_t("01:05"),
                    label=f"Сыроизготовитель {int(id)} (кор. мойка)",
                )
                yield

    def g3():
        with code("melters_and_baths"):
            lines_df = pd.DataFrame(index=["water", "salt"])
            lines_df["cleanings"] = [[] for _ in range(2)]
            if properties["mozzarella"].water_melting_end_time:
                lines_df.loc["water", "cleanings"].extend(
                    [
                        m.create_block("cleaning", size=(cast_t("02:20"), 0), label="Линия 1 плавилка"),
                        m.create_block("cleaning", size=(cast_t("01:30"), 0), label="Линия 1 ванна 1 + ванна 2"),
                    ]
                )
            else:
                # no water used
                m.row(
                    "cleaning",
                    push_func=AxisPusher(start_from=cast_t("10:00"), validator=CleaningValidator(ordered=False)),
                    size=cast_t("01:45"),
                    label=f"Линия 1 плавилка (кор. мойка)",
                )
                m.row(
                    "cleaning",
                    push_func=AxisPusher(start_from=cast_t("10:00"), validator=CleaningValidator(ordered=False)),
                    size=cast_t("01:15"),
                    label=f"Линия 1 ванна 1 + ванна 2 (кор. мойка)",
                )

            if properties["mozzarella"].salt_melting_end_time:
                lines_df.loc["salt", "cleanings"].extend(
                    [
                        m.create_block("cleaning", size=(cast_t("02:20"), 0), label="Линия 2 плавилка"),
                        m.create_block("cleaning", size=(cast_t("01:30"), 0), label="Линия 2 ванна 1"),
                        m.create_block("cleaning", size=(cast_t("01:30"), 0), label="Линия 2 ванна 2"),
                    ]
                )
            else:
                # no salt used
                m.row(
                    "cleaning",
                    push_func=AxisPusher(start_from=cast_t("10:00"), validator=CleaningValidator(ordered=False)),
                    size=cast_t("01:45"),
                    label=f"Линия 2 плавилка (кор. мойка)",
                )
                m.row(
                    "cleaning",
                    push_func=AxisPusher(start_from=cast_t("10:00"), validator=CleaningValidator(ordered=False)),
                    size=cast_t("01:15"),
                    label=f"Линия 2 ванна 1 (кор. мойка)",
                )
                m.row(
                    "cleaning",
                    push_func=AxisPusher(start_from=cast_t("10:00"), validator=CleaningValidator(ordered=False)),
                    size=cast_t("01:15"),
                    label=f"Линия 2 ванна 2 (кор. мойка)",
                )

            lines_df["melting_end"] = [
                cast_t(properties["mozzarella"].water_melting_end_time),
                cast_t(properties["mozzarella"].salt_melting_end_time),
            ]
            lines_df = lines_df.sort_values(by="melting_end")

            for i, row in lines_df.iterrows():
                for j, c in enumerate(row["cleanings"]):
                    if j == 0:
                        m.block(
                            c,
                            push_func=AxisPusher(
                                start_from=["max_end", row["melting_end"] + 12], validator=CleaningValidator()
                            ),
                        )  # add hour
                    else:
                        m.block(c, push_func=AxisPusher(start_from="max_end", validator=CleaningValidator()))
                    yield

            # make iterator longer
            for _ in range(5):
                yield

    def _should_make_last_short_cleaning():
        last_full_cleaning = max(m.root.find(label="Полная мойка термизатора"), key=lambda b: b.y[0])
        return last_full_cleaning.y[0] <= cast_t("21:00") and not is_tomorrow_day_off

    def f4():
        if _should_make_last_short_cleaning():
            b = m.row(
                "cleaning",
                push_func=AxisPusher(start_from=cast_t("21:00"), validator=CleaningValidator()),
                size=cast_t("01:00"),
                label="Короткая мойка термизатора",
            ).block
            assert cast_t("21:00") <= b.x[0] and b.y[0] <= cast_t("01:00:00"), "Short cleaning too bad"

    if not alternative:
        run_order([f1, g2()], order1)
        run_order([g3(), f4], order2)
    else:
        f1()
        run_order([f4, g2()], order1)

        it = g3()
        for _ in range(5):
            next(it)

    if _should_make_last_short_cleaning():
        # shift short cleaning to make it as late as possible
        short_cleaning = m.root.find(label="Короткая мойка термизатора")[-1]
        short_cleaning.detach_from_parent()
        push(
            m.root,
            short_cleaning,
            push_func=ShiftPusher(period=-1, start_from=cast_t("01:00:00")),
            validator=CleaningValidator(ordered=False),
        )

    if molder:
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from="max_end", validator=CleaningValidator()),
            size=cast_t("01:20"),
            label="Формовщик",
        )

    return m.root


def make_contour_3(properties, **kwargs):
    def value_function(b):
        try:
            return -b.y[0], -b.find_one(label="Короткая мойка термизатора").x[0]
        except:
            return -b.y[0]

    try:
        df = optimize(_make_contour_3, value_function, properties, alternative=False, **kwargs)
    except:
        logger.info("Running alternative contour 3")
        df = optimize(_make_contour_3, value_function, properties, alternative=True, **kwargs)

    return df.iloc[-1]["output"]


def make_contour_4(properties, is_tomorrow_day_off=False):
    m = BlockMaker("4 contour")

    with code("drenators"):

        def _make_drenators(values, cleaning_time, label_suffix="", force_pairs=False):
            # logic
            i = 0
            while i < len(values):
                drenator_id, drenator_end = values[i]
                if i == 0 and not force_pairs:
                    # run first drenator single if not force pairs
                    ids = [str(drenator_id)]
                    block = m.row(
                        "cleaning",
                        push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator(ordered=False)),
                        size=cast_t(cleaning_time),
                        ids=ids,
                        label=f'Дренатор {", ".join(ids)}{label_suffix}',
                    ).block
                else:
                    if i + 1 < len(values) and (
                        force_pairs or values[i + 1][1] <= block.y[0] + 2 and not is_tomorrow_day_off
                    ):
                        # run pair
                        ids = [str(drenator_id), str(values[i + 1][0])]
                        block = m.row(
                            "cleaning",
                            push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator(ordered=False)),
                            size=cast_t(cleaning_time),
                            ids=ids,
                            label=f'Дренатор {", ".join(ids)}{label_suffix}',
                        ).block
                        i += 1
                    else:
                        # run single
                        ids = [str(drenator_id)]
                        block = m.row(
                            "cleaning",
                            push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator(ordered=False)),
                            size=cast_t(cleaning_time),
                            ids=[drenator_id],
                            label=f'Дренатор {", ".join(ids)}{label_suffix}',
                        ).block
                i += 1

        with code("Main drenators"):
            # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
            values = properties["mozzarella"].drenator_times()
            for value in values:
                value[1] = cast_t(value[1])
                value[1] += 17  # add hour and 25 minutes of buffer
            values = list(sorted(values, key=lambda value: value[1]))

            _make_drenators(values, "01:20")
            used_ids = set([value[0] for value in values])

        with code("Non used drenators"):
            values = []
            # run drenators that are not present
            non_used_ids = set(range(1, 9)) - used_ids
            non_used_ids = [str(x) for x in non_used_ids]
            for non_used_id in non_used_ids:
                values.append([non_used_id, cast_t("10:00")])
            _make_drenators(values, "01:05", " (кор. мойка)", force_pairs=True)

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:30"),
        label="Транспортер + линия кислой сыворотки",
    )

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:30"),
        label="Линия кислой сыворотки",
    )

    return m.root


def make_contour_5(properties, input_tanks=None):
    input_tanks = input_tanks or [["4", 80], ["5", 80]]
    m = BlockMaker("5 contour")

    m.row("cleaning", push_func=add_push, size=cast_t("01:20"), label="Танк концентрата")

    m.row(
        "cleaning", push_func=AxisPusher(validator=CleaningValidator()), size=cast_t("01:20"), label="Танк концентрата"
    )

    with code("scotta"):
        start_t = cast_t("06:30")
        for id, volume in input_tanks:
            if not volume:
                continue
            concentration_t = custom_round(volume / 15 * 12, 1, "ceil")
            start_t += concentration_t
            m.row(
                "cleaning",
                push_func=AxisPusher(start_from=start_t, validator=CleaningValidator()),
                size=cast_t("01:20"),
                label=f"Танк рикотты",
            )

    m.row(
        "cleaning", push_func=AxisPusher(validator=CleaningValidator()), size=cast_t("01:20"), label="Линия Ретентата"
    )

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:20"),
        label="Линия подачи на НФ открыть кран",
    )

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("08:30"), validator=CleaningValidator(ordered=False)),
        size=cast_t("01:20"),
        label="Линия Концентрата на отгрузку",
    )

    return m.root


def make_contour_6(properties):
    m = BlockMaker("6 contour")

    if properties["milk_project"].is_present() or properties["adygea"].is_present():
        with code("calc end time"):
            values = []
            if properties["adygea"].is_present():
                values.append(properties["adygea"].end_time)
            if properties["milk_project"].is_present():
                values.append(properties["milk_project"].end_time)
            end_time = max(values)

        m.row(
            "cleaning",
            push_func=add_push,
            x=cast_t(end_time),
            size=cast_t("01:20"),
            label="Линия сырого молока на роникс",
        )

    with code("Танк рикотты 1 внутри дня"):
        whey_used = 1900 * properties["ricotta"].n_boilings
        if whey_used > 100000:
            m.row(
                "cleaning",
                push_func=AxisPusher(start_from=cast_t("12:00"), validator=CleaningValidator(ordered=False)),
                size=cast_t("01:20"),
                label="Танк рикотты (сладкая сыворотка)",
            )

    with code("cream tanks"):
        if properties["mascarpone"].fourth_boiling_group_adding_lactic_acid_time:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=cast_t(properties["mascarpone"].fourth_boiling_group_adding_lactic_acid_time) + 12,
                    validator=CleaningValidator(ordered=False),
                ),
                size=cast_t("01:20"),
                label="Танк сливок",
            )  # fourth mascarpone boiling group end + hour

        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t("09:00"), validator=CleaningValidator(ordered=False)),
            size=cast_t("01:20"),
            label="Танк сливок",
        )

    with code("mascarpone"):
        if properties["mascarpone"].is_present():
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=cast_t(properties["mascarpone"].last_pumping_off) + 6,
                    validator=CleaningValidator(ordered=False),
                ),
                size=(cast_t("01:20"), 0),
                label="Маскарпоне",
            )

    ricotta_end = cast_t(properties["ricotta"].last_pumping_out_time) or 0 + 12
    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator(ordered=False)),
        size=cast_t("02:30"),
        label="Линия сладкой сыворотки",
    )

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator(ordered=False)),
        size=cast_t("01:20"),
        label="Танк сливок",
    )  # ricotta end + hour

    with code("Танк рикотты 1"):
        m.row(
            "cleaning",
            push_func=AxisPusher(
                start_from=cast_t(properties["ricotta"].start_of_ninth_from_the_end_time)
                or 0,  # todo maybe: remove or 0, make properly
                validator=CleaningValidator(ordered=False),
            ),
            size=cast_t("01:20"),
            label="Танк рикотты (сладкая сыворотка)",
        )

    for label in ["Линия сливок на подмес рикотта", "Танк рикотты (скотта)", "Танк рикотты (сладкая сыворотка)"]:
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator(ordered=False)),
            size=cast_t("01:20"),
            label=label,
        )

    if properties["butter"].is_present():
        m.row(
            "cleaning",
            push_func=AxisPusher(
                start_from=cast_t(properties["butter"].end_time), validator=CleaningValidator(ordered=False)
            ),
            size=cast_t("01:20"),
            label="Маслоцех",
        )

    return m.root


def make_schedule(properties_by_department, **kwargs):
    m = BlockMaker("schedule")

    contours = [
        make_contour_1(properties_by_department),
        make_contour_2(properties_by_department),
        make_contour_3(
            properties_by_department,
            molder=kwargs.get("molder", False),
            is_tomorrow_day_off=kwargs.get("is_tomorrow_day_off", False),
        ),
        make_contour_4(properties_by_department, is_tomorrow_day_off=kwargs.get("is_tomorrow_day_off", False)),
        make_contour_5(properties_by_department, input_tanks=kwargs.get("input_tanks")),
        make_contour_6(properties_by_department),
    ]

    for contour in contours:
        m.col(contour, push_func=add_push)

    return m.root
