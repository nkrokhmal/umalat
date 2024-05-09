import types

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.pushers.pushers import add_push
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis

from lessmore.utils.easy_printing.print_json import print_json

from app.models import Washer, cast_model
from app.scheduler.time_utils import cast_t


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


def make_contour_1(properties: dict, basement_brine: bool = False, is_today_day_off: bool = False):
    # - Init block maker

    m = BlockMaker("1 contour")

    # - Process day off - clean, starting from 12:00

    if is_today_day_off:
        for duration, name in [
            ("01:15", "Танк Моцарелла и дозаторы"),
            ("01:00", "Танки роникс 1/2"),
            ("01:30", "Сырое молоко на адыгейский"),
            ("01:20", "Танк смесей"),
            ("00:55", "Линия подвал рассол"),
            ("01:20", "Танк сырого молока 1"),
            ("01:20", "Танк сырого молока 2"),
            ("00:55", "Линия приемки молока 1"),
            ("00:55", "Линия приемки молока 2"),
            ("00:55", "Линия отгрузки сырья"),
        ]:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=cast_t("12:00"),
                    validator=CleaningValidator(),
                ),
                size=cast_t(duration),
                label=name,
            )

        return m.root

    # - Танк “Моцарелла и дозаторы” (после фасовки на моцарелле в воде + 20 минут)

    if properties["mozzarella"].is_present:
        if properties["mozzarella"].water_packing_end_time:
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

    if properties["adygea"].is_present:
        m.row(
            "cleaning",
            push_func=AxisPusher(
                start_from=cast_t(properties["adygea"].end_time) + 12,  # После адыгейского + час
                validator=CleaningValidator(),
            ),
            size=cast_t("01:00"),
            label="Танки роникс 1/2",
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

    if properties["mozzarella"].is_present:
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


def make_contour_2(
    properties, naslavuchich: bool = False, is_today_day_off: bool = False, comet_rubber_end_time: str = ""
):
    m = BlockMaker("2 contour")

    # - Process day off - clean, starting from 12:00

    if is_today_day_off:
        for duration, name in [
            ("01:30", "Комет"),
            ("01:20", "Фасовочная вода"),
            ("01:10", "Танк жирной воды 1"),
            ("01:10", "Танк жирной воды 2"),
            ("01:10", "Жирная вода на сепаратор"),
            ("01:30", "Ванны моцарелла соль"),
            ("01:30", "Сливки от сепаратора жирной воды"),
            ("01:10", "Сливки отпастера 25"),
            ("01:10", "Линия обрата в сливки"),
            ("01:30", "Линия наславучич"),
        ]:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=cast_t("12:00"),
                    validator=CleaningValidator(),
                ),
                size=cast_t(duration),
                label=name,
            )

        return m.root

    # - Комет (После окончания фасовки на моцарелле в воде + 2 часа)

    if properties["mozzarella"].is_present:
        # -- Find time

        times = []
        if properties["mozzarella"].water_packing_end_time:
            times.append(cast_t(properties["mozzarella"].water_packing_end_time) + 24)
        if comet_rubber_end_time:
            times.append(cast_t(comet_rubber_end_time))

        # -- Make row

        if times:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=max(times),
                    validator=CleaningValidator(),
                ),
                size=cast_t("01:30"),
                label="Комет",
            )

    # - Фасовочная вода (После окончания фасовки на моцарелле в воде + 15 минут)

    if properties["mozzarella"].is_present:
        if properties["mozzarella"].water_packing_end_time:
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

    # - Жирная вода на сепаратор (по танков)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from="last_end",
            validator=CleaningValidator(),
        ),
        size=cast_t("01:10"),
        label="Жирная вода на сепаратор",
    )

    # - Ванны моцарелла соль (После окончания посолки на линии пиццы + 15 минут)

    if properties["mozzarella"].is_present:
        m.row(
            "cleaning",
            push_func=AxisPusher(
                start_from=cast_t(properties["mozzarella"].salt_melting_end_time) + 3,
                validator=CleaningValidator(),
            ),
            size=cast_t("01:30"),
            label="Ванны моцарелла соль",
        )

    # - Сливки от сепаратора жирной воды (После Ванны моцарелла соль)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from="last_end",
            validator=CleaningValidator(),
        ),
        size=cast_t("01:30"),
        label="Сливки от сепаратора жирной воды",
    )

    # - Сливки отпастера 25 (После Ванны моцарелла соль)

    m.row(
        "cleaning",
        push_func=AxisPusher(
            start_from="last_end",
            validator=CleaningValidator(),
        ),
        size=cast_t("01:10"),
        label="Сливки отпастера 25",
    )

    # - Линия обрата в сливки (После Ванны моцарелла соль)

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


def make_contour_3(properties: dict, is_today_day_off: bool = False):
    m = BlockMaker("3 contour")

    # - Process day off - clean, starting from 12:00

    if is_today_day_off:
        for duration, name in [
            (cast_model(Washer, "Длинная мойка термизатора").time // 5, "Полная мойка термизатора"),
            ("01:20", "Сыроизготовитель 1"),
            ("01:20", "Сыроизготовитель 2"),
            ("01:20", "Сыроизготовитель 3"),
            ("01:20", "Сыроизготовитель 4"),
            ("01:30", "Плавилка линия пицца чиз"),
            ("01:10", "Контур циркуляции рассола"),
            ("01:10", "Линия пицца чиз формовщик"),
        ]:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=cast_t("12:00"),
                    validator=CleaningValidator(),
                ),
                size=cast_t(duration),
                label=name,
            )

        return m.root

    # - Термизатор (короткие и длинные мойки)

    if properties["mozzarella"].is_present:
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

    # - Сыроизготовитель (Через 10 минут после того, как он слился)

    if properties["mozzarella"].is_present:
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

    #  Плавилка линия пицца чиз (конец плавления пицца чиз + 1 час)

    if properties["mozzarella"].is_present:
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

    if properties["mozzarella"].is_present:
        if properties["mozzarella"].bar12_present:
            m.row(
                "cleaning",
                push_func=AxisPusher(start_from="max_end", validator=CleaningValidator()),
                size=cast_t("01:10"),
                label="Линия пицца чиз формовщик",
            )

    return m.root


def make_contour_4(properties: dict, is_today_day_off: bool = False):
    m = BlockMaker("4 contour")

    # - Process day off - clean, starting from 12:00

    if is_today_day_off:
        for duration, name in [
            ("01:20", "Дренатор 1, 2"),
            ("01:20", "Дренатор 3, 4"),
            ("01:20", "Дренатор 5, 6"),
            ("01:20", "Дренатор 7, 8"),
            ("01:30", "Транспортер + линия кислой сыворотки"),
            ("01:30", "Линия кислой сыворотки"),
        ]:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=cast_t("12:00"),
                    validator=CleaningValidator(),
                ),
                size=cast_t(duration),
                label=name,
            )

        return m.root

    # - Дренаторы (сложная логика)

    if properties["mozzarella"].is_present:

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
                    if i + 1 < len(values) and (force_pairs or values[i + 1][1] <= block.y[0] + 2):
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
        values = list(sorted(values, key=lambda value: value[1]))
        _make_drenators(values, cleaning_time="01:20")

    # - Траспортер + линия кислой сыворотки (после дренаторов)

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:30"),
        label="Транспортер + линия кислой сыворотки",
    )

    # - Линия кислой сыворотки (после дренаторов)

    m.row(
        "cleaning",
        push_func=AxisPusher(validator=CleaningValidator()),
        size=cast_t("01:30"),
        label="Линия кислой сыворотки",
    )

    return m.root


def make_contour_5(properties: dict, is_today_day_off: bool = False):
    m = BlockMaker("5 contour")

    # - Process day off - clean, starting from 12:00

    if is_today_day_off:
        for duration, name in [
            ("01:20", "Танк рикотты 4"),
            ("01:20", "Танк рикотты 5"),
            ("01:20", "Танк рикотты 6"),
            ("01:20", "Танк рикотты 7"),
            ("01:20", "Танк рикотты 8"),
            ("00:55", "Линия подачи на НФ"),
            ("00:55", "Линия ретентата"),
            ("00:55", "Линия Концентрата на отгрузку"),
        ]:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=cast_t("12:00"),
                    validator=CleaningValidator(),
                ),
                size=cast_t(duration),
                label=name,
            )

        return m.root

    # - Танки рикотты 4-8

    for i, time in enumerate(["11:00", "15:30", "01:00", "20:00", "22:00"]):
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
            size=cast_t("01:20"),
            label=f"Танк рикотты {i + 4}",
        )

    # - Линия подачи на НФ (После танка рикотты 8)

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from="last_end", validator=CleaningValidator()),
        size=cast_t("00:55"),
        label="Линия подачи на НФ",
    )

    # - Линия ретентата (После танка рикотты 8)

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from="last_end", validator=CleaningValidator()),
        size=cast_t("00:55"),
        label="Линия ретентата",
    )

    # - Линия Концентрата на отгрузку (09:00, 18:00)

    for time in ["09:00", "18:00"]:
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
            size=cast_t("00:55"),
            label="Линия Концентрата на отгрузку",
        )

    return m.root


def make_contour_6(properties: dict, is_today_day_off: bool = False):
    m = BlockMaker("6 contour")

    # - Process day off - clean, starting from 12:00

    if is_today_day_off:
        for duration, name in [
            ("02:00", "Линия сладкой сыворотки"),
            ("01:20", "Танк рикотты 3"),
            ("01:20", "Танк рикотты 1-2"),
            ("01:20", "Танк сливок 1"),
            ("01:20", "Танк сливок 2"),
            ("01:20", "Танк сливок 3"),
            ("01:30", "Танк сливок 4"),
            ("01:00", "Линия сливок на маскарпоне"),
            ("00:55", "Линия сливок на подмес на рикотте"),
            ("02:50", "Линия сливок маслоцех + обратка"),
        ]:
            m.row(
                "cleaning",
                push_func=AxisPusher(
                    start_from=cast_t("12:00"),
                    validator=CleaningValidator(),
                ),
                size=cast_t(duration),
                label=name,
            )

        return m.root

    # - Линия сладкой сыворотки (Завершаем слив на рикотте + час)

    if properties["ricotta"].is_present:
        m.row(
            "cleaning",
            push_func=AxisPusher(
                start_from=cast_t(properties["ricotta"].last_pumping_out_time) + 12, validator=CleaningValidator()
            ),
            size=cast_t("02:00"),
            label="Линия сладкой сыворотки",
        )

    # - Танк рикотты 3 (после линии сладкой сыворотки)

    m.row(
        "cleaning",
        push_func=AxisPusher(start_from="last_end", validator=CleaningValidator()),
        size=cast_t("1:20"),
        label="Танк рикотты 3",
    )

    # - Танк рикотты 1-2 (каждые 5 наборов рикотты)

    if properties["ricotta"].is_present:
        for time in properties["ricotta"].every_5th_pouring_times:
            m.row(
                "cleaning",
                push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
                size=cast_t("1:20"),
                label="Танк рикотты 1-2",
            )

    # - Танки сливок (1-3) (9:00, 7:00, 15:00)

    for i, time in enumerate(["09:00", "07:00", "15:00"]):
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
            size=cast_t("1:20"),
            label=f"Танк сливок {i + 1}",
        )

    if properties["mascarpone"].is_present:
        # - Танк сливок 4/5 (после каждого 8-го набора маскарпоне)

        for i, time in enumerate(properties["mascarpone"].every_8t_of_separation):
            m.row(
                "cleaning",
                push_func=AxisPusher(start_from=cast_t(time), validator=CleaningValidator()),
                size=cast_t("1:30"),
                label=f"Танк сливок {i + 4}",
            )

        # - Линия сливок на маскарпоне (после танков сливок)

        m.row(
            "cleaning",
            push_func=AxisPusher(start_from="last_end", validator=CleaningValidator()),
            size=cast_t("1:00"),
            label=f"Линия сливок на маскарпоне",
        )

    # - Линия сливок на подмес на рикотте (после последнего набора рикотты + 10 минут)

    if properties["ricotta"].is_present:
        m.row(
            "cleaning",
            push_func=AxisPusher(
                start_from=cast_t(properties["ricotta"].last_pouring_time) + 2, validator=CleaningValidator()
            ),
            size=cast_t("0:55"),
            label=f"Линия сливок на подмес на рикотте",
        )

    # - После окончания работы маслоцеха + 30 минут

    if properties["butter"].is_present:
        m.row(
            "cleaning",
            push_func=AxisPusher(start_from=cast_t(properties["butter"].end_time) + 6, validator=CleaningValidator()),
            size=cast_t("02:50"),
            label=f"Линия сливок маслоцех + обратка",
        )

    return m.root


def make_schedule(
    properties: dict,
    naslavuchich: bool = True,
    basement_brine: bool = True,
    is_today_day_off: bool = False,
):
    m = BlockMaker("schedule")

    contours = [
        make_contour_1(properties, basement_brine=basement_brine, is_today_day_off=is_today_day_off),
        make_contour_2(properties, naslavuchich=naslavuchich, is_today_day_off=is_today_day_off),
        make_contour_3(properties, is_today_day_off=is_today_day_off),
        make_contour_4(properties, is_today_day_off=is_today_day_off),
        make_contour_5(properties, is_today_day_off=is_today_day_off),
        make_contour_6(properties, is_today_day_off=is_today_day_off),
    ]

    for contour in contours:
        m.col(contour, push_func=add_push)

    return m.root
