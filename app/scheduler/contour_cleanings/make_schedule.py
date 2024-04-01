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

from lessmore.utils.easy_printing.print_json import print_json

from app.models import Washer, cast_model
from app.scheduler.time_utils import cast_t


# todo maybe: put in more proper place [@marklidenberg]
def calc_scotta_input_tanks(ricotta_n_boilings, adygea_n_boilings, milk_project_n_boilings):
    total_scotta = (
        (1900 - 130) * ricotta_n_boilings + adygea_n_boilings * 370 + milk_project_n_boilings * 2400
    )  # todo maybe: take from parameters [@marklidenberg]

    assert (
        total_scotta < 80000 + 60000 + 60000
    ), "Скотты больше, чем могут вместить танки. "  # todo maybe: take from parameters [@marklidenberg]

    left_scotta = total_scotta
    values = [["4", 0.0], ["5", 0.0], ["8", 0.0]]
    for value in values:
        cur_scotta = min(80000, left_scotta)
        value[1] = cur_scotta / 1000.0  # value in ton
        left_scotta -= cur_scotta
    return values


class CleaningValidator(ClassValidator):
    def __init__(self, window=30, ordered=False):
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


def make_contour_1(properties: dict, basement_brine: bool = False):
    # - Init block maker

    m = BlockMaker("1 contour")
    print_json(dict(properties["mozzarella"]))

    # - Танк “Моцарелла и дозаторы” (после фасовки на моцарелле в воде + 20 минут)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from=cast_t(properties["mozzarella"].water_packing_end_time)
            + 4,  # Моем после того, как закончилась фасовка на моцарелле в воде через 20 минут
            validator=CleaningValidator(),
        ),
        size=cast_t("01:15"),
        label="Танк Моцарелла и дозаторы",
    )

    # - Танки роникс 1/2 (после адыгейского + час)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from=cast_t(properties["adygea"].end_time) + 12,  # После адыгейского + час
            validator=CleaningValidator(),
        ),
        size=cast_t("01:00"),
        label="Танки роникс 1/2",  # todo later: question: тут одна мойка? Конец адыгейского - это какой момент точно? [@marklidenberg]
    )

    # - Сырое молоко на адыгейский (после роникса)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from="last_end",
            validator=CleaningValidator(),
        ),
        size=cast_t("01:30"),
        label="Сырое молоко на адыгейский",  # после роникса
    )

    # - Танки смесей (по 8-му наливу по каждой смеси и в конце смеси)

    times = sum([times for times in properties["mozzarella"].every_8th_pouring_end.values()], [])
    times = sorted([cast_t(time) for time in times])

    for i, time in enumerate(times):
        m.row(
            "cleaning",
            push_func=AxisPusher(
                start_from=time,
                validator=CleaningValidator(),
            ),
            size=cast_t("01:20"),
            label=f"Танк смесей",
        )

    # - Линия подвал рассол (07:00)

    if basement_brine:
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t("07:00"), validator=CleaningValidator()),
            size=cast_t("00:55"),
            label="Линия подвал рассол",
        )

    # - Танки сырого молока (11:00, 17:00, 22:00)

    for i, time in enumerate(["11:00", "17:00", "22:00"]):
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
            size=cast_t("01:20"),
            label=f"Танк сырого молока {i + 1}",
        )

    # - Линия приемки молока (03:00, 04:00)

    for i, time in enumerate(["03:00", "04:00"]):
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
            size=cast_t("00:55"),
            label=f"Линия приемки молока {i + 1}",
        )

    # - Линия отгрузки сырья (00:00)

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("00:00"), validator=CleaningValidator()),
        size=cast_t("00:55"),
        label="Линия отгрузки сырья",
    )

    return m.root


def make_contour_2(properties, naslavuchich: bool = False):
    m = BlockMaker("2 contour")

    # - Комет (После окончания фасовки на моцарелле в воде + 2 часа)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from=cast_t(properties["mozzarella"].water_packing_end_time) + 24,
            validator=CleaningValidator(),
        ),
        size=cast_t("01:30"),
        label="Комет",
    )

    # - Фасовочная вода (После окончания фасовки на моцарелле в воде + 15 минут)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from=cast_t(properties["mozzarella"].water_packing_end_time) + 3,
            validator=CleaningValidator(),
        ),
        size=cast_t("01:20"),
        label="Фасовочная вода",
    )

    # - Танки жирной воды (22:00, 07:00)

    for i, time in enumerate(["22:00", "07:00"]):
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
            size=cast_t("01:10"),
            label=f"Танк жирной воды {i + 1}",
        )

    # - Жирная вода на сепаратор (вода) (После окончания плавления на линии воды + 1 час)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from=cast_t(properties["mozzarella"].water_melting_end_time) + 12,
            validator=CleaningValidator(),
        ),
        size=cast_t("01:10"),
        label="Жирная вода на сепаратор (вода)",
    )

    # - Ванны моцарелла соль (После окончания посолки на линии пиццы + 15 минут)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from=cast_t(properties["mozzarella"].salt_melting_end_time) + 3,
            validator=CleaningValidator(),
        ),
        size=cast_t("01:30"),
        label="Ванны моцарелла соль",
    )

    # - Жирная вода на сепаратор (соль) (по порядку)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from="last_end",
            validator=CleaningValidator(),
        ),
        size=cast_t("01:10"),
        label="Жирная вода на сепаратор (соль)",
    )

    # - Сливки от сепаратора жирной воды (по порядку)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from="last_end",
            validator=CleaningValidator(),
        ),
        size=cast_t("01:30"),
        label="Сливки от сепаратора жирной воды",
    )

    # - Сливки отпастера 25(по порядку)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from="last_end",
            validator=CleaningValidator(),
        ),
        size=cast_t("01:10"),
        label="Сливки отпастера 25",
    )

    # - Линия обрата в сливки (по порядку)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from="last_end",
            validator=CleaningValidator(),
        ),
        size=cast_t("01:10"),
        label="Линия обрата в сливки",
    )

    # - Линия наславучич (18:00, с галочкой)

    if naslavuchich:
        m.row(
            "cleaning",
            push_func=AxisPusher(
                start_from=cast_t("18:00"),
                validator=CleaningValidator(),
            ),
            size=cast_t("01:30"),
            label="Линия наславучич",
        )

    return m.root


def make_contour_3(properties):
    m = BlockMaker("3 contour")

    # - Сыроизготовитель (Через 10 минут после того, как он слился)

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
            push_func=AxisPusher(
                start_from=cast_t(cheese_maker_end) + 1, validator=CleaningValidator()
            ),  # 10 minutes after pouring_off, 5 minutes after boiling ens
            size=cast_t("01:20"),
            label=f"Сыроизготовитель {int(n)}",
        )

    # - Термизатор (короткие и длинные мойки)

    for cleaning_time in properties["mozzarella"].short_cleaning_times:
        m.row(
            "cleaning",
            push_func=add_push,
            size=cast_model(Washer, "Короткая мойка термизатора").time // 5,
            x=cast_t(cleaning_time),
            label="Короткая мойка термизатора",
        )

    for cleaning_time in properties["mozzarella"].full_cleaning_times:
        m.row(
            "cleaning",
            push_func=add_push,
            size=cast_model(Washer, "Длинная мойка термизатора").time // 5,
            x=cast_t(cleaning_time),
            label="Полная мойка термизатора",
        )

    # - Плавилка линия пицца чиз (конец плавления пицца чиз + 1 час)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from=cast_t(properties["mozzarella"].salt_melting_end_time) + 12,
            validator=CleaningValidator(),
        ),
        size=cast_t("01:30"),
        label="Плавилка линия пицца чиз",
    )

    # - Контур циркуляции рассола (08:00)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from=cast_t("08:00"),
            validator=CleaningValidator(),
        ),
        size=cast_t("01:10"),
        label="Контур циркуляции рассола",
    )

    # - Линия пицца чиз формовщик (Если есть брус, то ставим мойку формовщика. Если линия занята - то после всех объектов)

    if properties["mozzarella"].bar12_present:
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from="max_end", validator=CleaningValidator()),
            size=cast_t("01:10"),
            label="Линия пицца чиз формовщик",
        )

    return m.root


def make_contour_4(properties, is_tomorrow_day_off=False):
    m = BlockMaker("4 contour")

    # - Дренаторы (сложная логика)

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
                    push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator()),
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
                        push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator()),
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
                        push_func=AxisPusher(start_from=drenator_end, validator=CleaningValidator()),
                        size=cast_t(cleaning_time),
                        ids=[drenator_id],
                        label=f'Дренатор {", ".join(ids)}{label_suffix}',
                    ).block
            i += 1

    # get when drenators end: [[3, 96], [2, 118], [4, 140], [1, 159], [5, 151], [7, 167], [6, 180], [8, 191]]
    values = properties["mozzarella"].drenator_times()
    for value in values:
        value[1] = cast_t(value[1])
        value[1] += 17  # add hour and 25 minutes of buffer
    values = list(sorted(values, key=lambda value: value[1]))
    _make_drenators(values, cleaning_time="01:20")

    # - Траспортер + линия кислой сыворотки (по порядку)

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:30"),
        label="Транспортер + линия кислой сыворотки",
    )

    # - Линия кислой сыворотки (по порядку)

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:30"),
        label="Линия кислой сыворотки",
    )

    return m.root


def make_contour_5(properties, input_tanks=None):
    m = BlockMaker("5 contour")

    # - Танки рикотты 4-8

    for i, time in enumerate(["11:00", "15:30", "01:00", "20:00", "22:00"]):
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
            size=cast_t("01:20" if i + 4 != 8 else "01:30"),
            label=f"Танк рикотты {i + 4}",
        )

    # - Линия подачи на НФ (по порядку)

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from="last_end", validator=CleaningValidator()),
        size=cast_t("00:55"),
        label="Линия подачи на НФ",
    )
    # - Линия ретентата (по порядку)

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from="last_end", validator=CleaningValidator()),
        size=cast_t("00:55"),
        label="Линия ретентата",
    )

    # - Линия Концентрата на отгрузку (08:30)

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from=cast_t("08:30"), validator=CleaningValidator()),
        size=cast_t("00:55"),
        label="Линия Концентрата на отгрузку",
    )

    return m.root


def make_contour_6(properties):
    m = BlockMaker("6 contour")
    #
    # # - Линия сырого молока на роникс
    #
    # if properties["milk_project"].is_present() or properties["adygea"].is_present():
    #     with code("calc end time"):
    #         values = []
    #         if properties["adygea"].is_present():
    #             values.append(properties["adygea"].end_time)
    #         if properties["milk_project"].is_present():
    #             values.append(properties["milk_project"].end_time)
    #         end_time = max(values)
    #
    #     m.row(
    #         "cleaning",
    #         push_func=add_push,
    #         x=cast_t(end_time),
    #         size=cast_t("01:20"),
    #         label="Линия сырого молока на роникс",
    #     )
    #
    # # - Танк рикотты 1 внутри дня
    #
    # whey_used = 1900 * properties["ricotta"].n_boilings
    # if whey_used > 100000:
    #     m.row(
    #         "cleaning",
    #         push_func=AxisPusher(start_from=cast_t("12:00"), validator=CleaningValidator()),
    #         size=cast_t("01:20"),
    #         label="Танк рикотты (сладкая сыворотка)",
    #     )
    #
    # # - Cream tanks
    #
    # if properties["mascarpone"].fourth_boiling_group_adding_lactic_acid_time:
    #     m.row(
    #         "cleaning",
    #         push_func=AxisPusher(
    #             start_from=cast_t(properties["mascarpone"].fourth_boiling_group_adding_lactic_acid_time) + 12,
    #             validator=CleaningValidator(),
    #         ),
    #         size=cast_t("01:20"),
    #         label="Танк сливок",
    #     )  # fourth mascarpone boiling group end + hour
    #
    # m.row(
    #     "cleaning",
    #     push_func=AxisPusher(start_from=cast_t("09:00"), validator=CleaningValidator()),
    #     size=cast_t("01:20"),
    #     label="Танк сливок",
    # )
    #
    # # - Маcкарпоне
    #
    # if properties["mascarpone"].is_present():
    #     m.row(
    #         "cleaning",
    #         push_func=AxisPusher(
    #             start_from=cast_t(properties["mascarpone"].last_pumping_off) + 6,
    #             validator=CleaningValidator(),
    #         ),
    #         size=(cast_t("01:20"), 0),
    #         label="Маскарпоне",
    #     )
    #
    # # - Линия сладкой сыворотки
    #
    # ricotta_end = cast_t(properties["ricotta"].last_pumping_out_time) or 0 + 12
    # m.row(
    #     "cleaning",
    #     push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator()),
    #     size=cast_t("02:30"),
    #     label="Линия сладкой сыворотки",
    # )
    #
    # # - Танк сливок
    #
    # m.row(
    #     "cleaning",
    #     push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator()),
    #     size=cast_t("01:20"),
    #     label="Танк сливок",
    # )  # ricotta end + hour
    #
    # # - Танк рикотты (сладкая сыворотка)
    #
    # m.row(
    #     "cleaning",
    #     push_func=AxisPusher(
    #         start_from=cast_t(properties["ricotta"].start_of_ninth_from_the_end_time)
    #         or 0,  # todo maybe: remove or 0, make properly [@marklidenberg]
    #         validator=CleaningValidator(),
    #     ),
    #     size=cast_t("01:20"),
    #     label="Танк рикотты (сладкая сыворотка)",
    # )
    #
    # # - Танк рикотты (скотта)
    #
    # for label in ["Линия сливок на подмес рикотта", "Танк рикотты (скотта)", "Танк рикотты (сладкая сыворотка)"]:
    #     m.row(
    #         "cleaning",
    #         push_func=AxisPusher(start_from=ricotta_end, validator=CleaningValidator()),
    #         size=cast_t("01:20"),
    #         label=label,
    #     )
    #
    # # - Маслоцех
    #
    # if properties["butter"].is_present():
    #     m.row(
    #         "cleaning",
    #         push_func=AxisPusher(
    #             start_from=cast_t(properties["butter"].end_time), validator=CleaningValidator()
    #         ),
    #         size=cast_t("01:20"),
    #         label="Маслоцех",
    #     )

    return m.root


def make_schedule(properties_by_department, **kwargs):
    m = BlockMaker("schedule")

    contours = [
        make_contour_1(properties_by_department),
        make_contour_2(properties_by_department),
        make_contour_3(
            properties_by_department,
        ),
        make_contour_4(properties_by_department, is_tomorrow_day_off=kwargs.get("is_tomorrow_day_off", False)),
        make_contour_5(properties_by_department, input_tanks=kwargs.get("input_tanks")),
        make_contour_6(properties_by_department),
    ]

    for contour in contours:
        m.col(contour, push_func=add_push)

    return m.root
