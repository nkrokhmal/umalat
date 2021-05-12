import openpyxl
import pandas as pd
from app.enum import LineName

from app.schedule_maker.departments.mozarella.frontend.drawing import *
from app.schedule_maker.departments.mozarella.frontend.style import *
from utils_ak.interactive_imports import *


def calc_form_factor_label(form_factors):
    form_factors = remove_neighbor_duplicates(form_factors)
    cur_label = None
    values = []
    for ff in form_factors:
        label = ""

        s = ""
        if label != cur_label:
            s += label + " "
            cur_label = label

        s += ff.name

        values.append(s)
    return "/".join(values)


def calc_group_form_factor_label(skus):
    skus = remove_neighbor_duplicates(skus)
    cur_label = None
    cur_form_factor = None
    values = []
    for sku in skus:

        if len(skus) == 1:
            label = sku.group.name
        else:
            label = sku.group.short_name

        s = ""
        if label != cur_label:
            s += label + " "
            cur_label = label
            # reset form factor also
            cur_form_factor = None

        if "Терка" in sku.form_factor.name:
            form_factor = "Терка"
        else:
            form_factor = sku.form_factor.name

        if cur_form_factor != form_factor:
            s += form_factor
            cur_form_factor = form_factor
        if s:
            values.append(s)
    return "/".join(values)


def make_header(date, start_time="01:00"):
    maker, make = init_block_maker("header", axis=1)

    with make("header", size=(0, 1), index_width=2):
        make(size=(1, 1), text="График наливов")
        make(size=(1, 1), text=cast_str(date, "%d.%m.%Y"), bold=True)
        for i in range(566):
            cur_time = cast_time(i + cast_t(start_time))
            days, hours, minutes = cur_time.split(":")
            if cur_time[-2:] == "00":
                make(
                    size=(1, 1),
                    text=str(int(hours)),
                    color=(218, 150, 148),
                    text_rotation=90,
                    font_size=9,
                )
            else:
                make(
                    size=(1, 1),
                    text=minutes,
                    color=(204, 255, 255),
                    text_rotation=90,
                    font_size=9,
                )
    return maker.root["header"]


def make_cheese_makers(master, rng):
    maker, make = init_block_maker("cheese_makers", axis=1)

    for i in rng:
        with make(f"cheese_maker", is_parent_node=True):
            with make("header", index_width=0, start_time="00:00", push_func=add_push):
                make(
                    "template",
                    x=(1, 0),
                    size=(3, 2),
                    text=f"Сыроизготовитель №1 Poly {i + 1}",
                    color=(183, 222, 232),
                    push_func=add_push,
                )

            for boiling in master.iter(cls="boiling", pouring_line=str(i)):
                boiling_model = boiling.props["boiling_model"]

                standard_boiling_volume = (
                    1000 if boiling_model.line.name == LineName.WATER else 850
                )  # todo: make properly
                boiling_size = int(
                    round(
                        8000
                        * boiling.props.relative_props.get(
                            "boiling_volume", standard_boiling_volume
                        )
                        / standard_boiling_volume
                    )
                )  # todo: make properly

                # [cheesemakers.boiling_params]
                boiling_label = "{} {} {} {}кг".format(
                    boiling_model.percent,
                    boiling_model.ferment,
                    "" if boiling_model.is_lactose else "безлактозная",
                    boiling_size,
                )

                with make(
                    "pouring_block",
                    boiling_label=boiling_label,
                    boiling_id=boiling.props["boiling_id"],
                    x=(boiling["pouring"].x[0], 0),
                    push_func=add_push,
                    axis=1,
                ):
                    with make():
                        make(
                            "termizator",
                            size=(boiling["pouring"]["first"]["termizator"].size[0], 1),
                        )
                        make(
                            "pouring_name",
                            size=(
                                boiling["pouring"].size[0]
                                - boiling["pouring"]["first"]["termizator"].size[0],
                                1,
                            ),
                            boiling_label=boiling_label,
                        )
                    with make(font_size=8):
                        make(
                            "pouring_and_fermenting",
                            size=(
                                boiling["pouring"]["first"]["termizator"].size[0]
                                + boiling["pouring"]["first"]["fermenting"].size[0],
                                1,
                            ),
                            push_func=add_push,
                        )
                        make(
                            "soldification",
                            size=(
                                boiling["pouring"]["first"]["soldification"].size[0],
                                1,
                            ),
                        )
                        make(
                            "cutting",
                            size=(boiling["pouring"]["first"]["cutting"].size[0], 1),
                        )
                        make(
                            "pumping_out",
                            size=(
                                boiling["pouring"]["first"]["pumping_out"].size[0],
                                1,
                            ),
                        )
                        make(
                            "pouring_off",
                            size=(
                                boiling["pouring"]["second"]["pouring_off"].size[0],
                                1,
                            ),
                        )
                        make(
                            "extra",
                            size=(boiling["pouring"]["second"]["extra"].size[0], 1),
                        )
        # add two lines for "Расход пара"
        make("stub", size=(0, 2))

    return maker.root


def make_cleanings(master):
    maker, make = init_block_maker("cleanings_row", is_parent_node=True, axis=1)

    with make("header", index_width=0, start_time="00:00", push_func=add_push):
        make(
            "template",
            x=(1, 0),
            size=(3, 2),
            text="Мойка термизатора",
            color="white",
            bold=True,
            push_func=add_push,
        )

    for cleaning in master.iter(cls="cleaning"):
        b = maker.copy(cleaning, with_props=True)
        b.props.update(size=(b.props["size"][0], 2))
        make(b, push_func=add_push)
    # add two lines for "Расход пара"
    make("stub", size=(0, 2))
    return maker.root


def make_multihead_cleanings(master):
    maker, make = init_block_maker(
        "multihead_cleanings_row", is_parent_node=True, axis=1
    )
    for multihead_cleaning in master.iter(cls="multihead_cleaning"):
        b = maker.copy(multihead_cleaning, with_props=True)
        b.props.update(size=(b.props["size"][0], 1))
        make(b, push_func=add_push)
    return maker.root


def make_meltings_1(master, line_name, title, coolings_mode="all"):
    maker, make = init_block_maker("melting", axis=1)

    with make("header", start_time="00:00", push_func=add_push):
        make(
            "template",
            index_width=0,
            x=(1, 0),
            size=(3, 2),
            text=title,
            push_func=add_push,
        )

    with make("melting_row", push_func=add_push, is_parent_node=True):
        for boiling in master.iter(
            cls="boiling", boiling_model=lambda bm: bm.line.name == line_name
        ):
            form_factor_label = calc_form_factor_label(
                [
                    melting_process.props["bff"]
                    for melting_process in boiling.iter(cls="melting_process")
                ]
            )

            with make(
                "melting_block",
                axis=1,
                boiling_id=boiling.props["boiling_id"],
                push_func=add_push,
                form_factor_label=form_factor_label,
            ):
                with make("serving_row"):
                    make(
                        "serving",
                        x=(
                            boiling["melting_and_packing"]["melting"]["serving"].x[0],
                            0,
                        ),
                        size=(
                            boiling["melting_and_packing"]["melting"]["serving"].size[
                                0
                            ],
                            1,
                        ),
                        push_func=add_push,
                    )

                with make("label_row"):
                    make(
                        "serving",
                        x=(
                            boiling["melting_and_packing"]["melting"]["serving"].x[0],
                            0,
                        ),
                        size=(
                            boiling["melting_and_packing"]["melting"]["serving"].size[
                                0
                            ],
                            1,
                        ),
                        visible=False,
                        push_func=add_push,
                    )
                    make("melting_label", size=(4, 1))

                    # todo: make properly
                    assert (
                        boiling["melting_and_packing"]["melting"]["meltings"].size[0]
                        >= 5
                    ), "В расписании есть блок плавления меньше 5 блоков. Такой случай пока не обработан. "

                    make(
                        "melting_name",
                        size=(
                            boiling["melting_and_packing"]["melting"]["meltings"].size[
                                0
                            ]
                            - 4,
                            1,
                        ),
                        form_factor_label=boiling.props["form_factor_label"],
                    )

                with make("melting_row"):
                    make(
                        "melting_process",
                        x=(
                            boiling["melting_and_packing"]["melting"]["meltings"].x[0],
                            0,
                        ),
                        size=(
                            boiling["melting_and_packing"]["melting"]["meltings"].size[
                                0
                            ],
                            1,
                        ),
                        speed=900,
                        push_func=add_push,
                    )

    n_cooling_lines = 0
    make("cooling_row", axis=1, is_parent_node=True)
    cooling_lines = []

    for boiling in master.iter(
        cls="boiling", boiling_model=lambda bm: bm.line.name == line_name
    ):
        class_validator = ClassValidator(window=10)

        def validate(b1, b2):
            validate_disjoint_by_axis(b1, b2)

        class_validator.add("cooling_block", "cooling_block", validate)

        cooling_label = "cooling" if line_name == LineName.WATER else "salting"

        cur_cooling_size = None
        for i, cooling_process in enumerate(
            listify(
                boiling["melting_and_packing"]["melting"]["coolings"]["cooling_process"]
            )
        ):
            start_from = listify(cooling_process["start"]["cooling"])[0].x[0]
            cooling_block = maker.create_block(
                "cooling_block", x=(start_from, 0)
            )  # todo: create dynamic x calculation when empty block

            for cooling in listify(cooling_process["start"]["cooling"]):
                block = maker.create_block(
                    cooling_label,
                    size=(cooling.size[0], 1),
                    x=[cooling.x[0] - start_from, 0],
                )
                push(cooling_block, block, push_func=add_push)

            if coolings_mode == "all":
                cur_cooling_size = cooling_block.size[0]
            elif coolings_mode == "unique":
                if cur_cooling_size == cooling_block.size[0]:
                    continue
            elif coolings_mode == "first":
                if i >= 1:
                    continue

            # try to add to the earliest line as possible
            j = 0
            while True:
                if j == n_cooling_lines:
                    n_cooling_lines += 1
                    new_cooling_line = maker.create_block(
                        "cooling_line", is_parent_node=True, size=(0, 1)
                    )
                    cooling_lines.append(new_cooling_line)
                    push(maker.root["cooling_row"], new_cooling_line)

                res = simple_push(
                    cooling_lines[j], cooling_block, validator=class_validator
                )
                if isinstance(res, Block):
                    # pushed block successfully
                    break
                j += 1

                if n_cooling_lines == 100:
                    raise AssertionError("Создано слишком много линий охлаждения.")

    # add two lines for "Расход пара"
    make("stub", size=(0, 2))
    return maker.root


def make_shifts(start_from, shifts):
    maker, make = init_block_maker("shifts", start_time="00:00", x=[start_from, 0])

    for shift in shifts:
        shift.setdefault("color", (149, 179, 215))
        make("shift", **shift)
    return maker.root


def make_melting(boiling, line_name):
    maker, make = init_block_maker("meltings", axis=1)

    form_factor_label = calc_form_factor_label(
        [
            melting_process.props["bff"]
            for melting_process in boiling.iter(cls="melting_process")
        ]
    )
    cooling_label = "cooling" if line_name == LineName.WATER else "salting"

    with make(
        "melting_block",
        axis=1,
        boiling_id=boiling.props["boiling_id"],
        form_factor_label=form_factor_label,
        push_func=add_push,
    ):
        with make(
            "label_row",
            x=(boiling["melting_and_packing"]["melting"]["serving"].x[0], 0),
            push_func=add_push,
        ):
            make(
                "melting_label",
                size=(4, 1),
                block_front_id=boiling.props["block_front_id"],
            )
            assert (
                boiling["melting_and_packing"]["melting"].size[0] >= 5
            ), "В расписании есть блок плавления меньше 5 блоков. Такой случай пока не обработан. "
            make(
                "melting_name",
                size=(boiling["melting_and_packing"]["melting"].size[0] - 4, 1),
                form_factor_label=boiling.props["form_factor_label"],
            )

        with make("melting_row"):
            make(
                "serving",
                x=(boiling["melting_and_packing"]["melting"]["serving"].x[0], 0),
                size=(boiling["melting_and_packing"]["melting"]["serving"].size[0], 1),
                push_func=add_push,
            )
            make(
                "melting_process",
                x=(boiling["melting_and_packing"]["melting"]["meltings"].x[0], 0),
                size=(boiling["melting_and_packing"]["melting"]["meltings"].size[0], 1),
                speed=900,
                push_func=add_push,
            )
            make(
                cooling_label,
                size=(
                    listify(
                        boiling["melting_and_packing"]["melting"]["coolings"][
                            "cooling_process"
                        ]
                    )[-1]["start"].size[0],
                    1,
                ),
            )

        with make("cooling_row"):
            make(
                cooling_label,
                x=(
                    listify(
                        boiling["melting_and_packing"]["melting"]["coolings"][
                            "cooling_process"
                        ]
                    )[0]["start"].x[0],
                    0,
                ),
                size=(
                    listify(
                        boiling["melting_and_packing"]["melting"]["coolings"][
                            "cooling_process"
                        ]
                    )[0]["start"].size[0],
                    1,
                ),
                push_func=add_push,
            )
    return maker.root


def make_meltings_2(master, line_name, title):
    # todo: make dynamic lines
    maker, make = init_block_maker("melting", axis=1)

    n_lines = 5

    melting_lines = []
    for i in range(n_lines):
        melting_lines.append(
            make(f"salt_melting_{i}", size=(0, 3), is_parent_node=True).block
        )
        # add line for "Расход пара"
        make("stub", size=(0, 1))

    make(
        "template",
        index_width=0,
        x=(1, melting_lines[0].x[1]),
        size=(3, 6),
        start_time="00:00",
        text=title,
        push_func=add_push,
    )

    for i, boiling in enumerate(
        master.iter(cls="boiling", boiling_model=lambda bm: bm.line.name == line_name)
    ):
        push(
            melting_lines[i % n_lines],
            make_melting(boiling, line_name),
            push_func=add_push,
        )
    return maker.root


def make_packing_block(packing_block, boiling_id):
    skus = [
        packing_process.props["sku"]
        for packing_process in packing_block.iter(cls="process")
    ]
    group_form_factor_label = calc_group_form_factor_label(skus)
    brand_label = "/".join(remove_neighbor_duplicates([sku.brand_name for sku in skus]))
    maker, make = init_block_maker(
        "packing_block",
        x=(packing_block.x[0], 0),
        boiling_id=boiling_id,
        push_func=add_push,
        axis=1,
        brand_label=brand_label,
        group_form_factor_label=group_form_factor_label,
    )
    with make():
        if packing_block.size[0] >= 4:
            make("packing_label", size=(3, 1))
            make("packing_name", size=(packing_block.size[0] - 3, 1))
        else:
            # todo: make properly
            make("packing_name", size=(packing_block.size[0], 1))

    with make():
        make("packing_brand", size=(packing_block.size[0], 1))

    with make(is_parent_node=True):
        for packing_process in packing_block.iter(cls="process"):
            make(
                "packing_process",
                x=(packing_process.props["x_rel"][0], 0),
                size=(packing_process.size[0], 1),
                push_func=add_push,
            )
        for conf in packing_block.iter(cls="packing_configuration"):
            make(
                "packing_configuration",
                x=(conf.props["x_rel"][0], 0),
                size=(conf.size[0], 1),
                push_func=add_push,
            )
    return maker.root


def make_packings(master, line_name):
    maker, make = init_block_maker("packing", axis=1)

    for packing_team_id in range(1, 3):
        with make("packing_team", size=(0, 3), axis=0, is_parent_node=True):
            for boiling in master.iter(
                cls="boiling", boiling_model=lambda bm: bm.line.name == line_name
            ):
                for packing_block in boiling.iter(
                    cls="collecting", packing_team_id=packing_team_id
                ):
                    make(
                        make_packing_block(packing_block, boiling.props["boiling_id"]),
                        push_func=add_push,
                    )
            try:
                for conf in listify(master["packing_configuration"]):
                    # first level only
                    if (
                        conf.props["packing_team_id"] != packing_team_id
                        or conf.props["line_name"] != line_name
                    ):
                        continue
                    make(
                        "packing_configuration",
                        x=(conf.props["x"][0], 2),
                        size=(conf.size[0], 1),
                        push_func=add_push,
                    )
            except:
                # no packing_configuration in schedule first level
                pass
    return maker.root


def make_extra_packings(extra_packings):
    maker, make = init_block_maker("packing", axis=1, is_parent_node=True)
    for packing_block in extra_packings.iter(cls="packing"):
        make(
            make_packing_block(packing_block, packing_block.props["boiling_id"]),
            push_func=add_push,
        )
    return maker.root


def make_frontend(schedule, coolings_mode="first"):
    master = schedule["master"]
    extra_packings = schedule["extra_packings"]

    maker, make = init_block_maker("root", axis=1)

    make("stub", size=(0, 1))

    start_t = min(
        [boiling.x[0] for boiling in listify(master["boiling"])]
    )  # first pouring time
    start_t = int(custom_round(start_t, 12, "floor"))  # round to last hour
    start_t -= 24
    start_time = cast_time(start_t)
    make(make_header(schedule.props["date"], start_time=start_time))

    with make("pouring", start_time=start_time, axis=1):
        make(
            make_shifts(
                0,
                [
                    {"size": (cast_t("19:00") - cast_t("07:00"), 1), "text": "1 смена"},
                    {
                        "size": (
                            cast_t("01:03:00") - cast_t("19:00") + 1 + cast_t("05:30"),
                            1,
                        ),
                        "text": "2 смена",
                    },
                ],
            )
        )
        make(make_cheese_makers(master, range(2)))
        # make(make_shifts(0, [{'size': (cast_t('19:00') - cast_t('07:00'), 1), 'text': '1 смена'},
        #                      {'size': (cast_t('01:03:00') - cast_t('19:00') + 1 + cast_t('05:30'), 1), 'text': '2 смена'}]))
        make(make_cleanings(master))
        make(make_cheese_makers(master, range(2, 4)))
        make(
            make_shifts(
                0,
                [
                    {
                        "size": (cast_t("19:05") - cast_t("07:00"), 1),
                        "text": "Оператор + Помощник",
                    }
                ],
            )
        )

    start_t = min(
        [boiling["melting_and_packing"].x[0] for boiling in listify(master["boiling"])]
    )  # first melting time
    start_t = int(custom_round(start_t, 12, "floor"))  # round to last hour
    start_t -= 24
    start_time = cast_time(start_t)
    make(make_header(schedule.props["date"], start_time=start_time))

    with make("melting", start_time=start_time, axis=1):
        make(make_multihead_cleanings(master))
        make(
            make_meltings_1(
                master,
                LineName.WATER,
                "Линия плавления моцареллы в воде №1",
                coolings_mode=coolings_mode,
            )
        )
        # make(make_meltings_2(schedule, LineName.WATER, 'Линия плавления моцареллы в воде №1'))
        make(
            make_shifts(
                0,
                [
                    {
                        "size": (cast_t("19:05") - cast_t("07:00"), 1),
                        "text": "бригадир упаковки + 5 рабочих",
                    }
                ],
            )
        )
        make(make_packings(master, LineName.WATER))
        make(
            make_shifts(
                0,
                [
                    {
                        "size": (cast_t("19:00") - cast_t("07:00"), 1),
                        "text": "1 смена оператор + помощник",
                    },
                    {
                        "size": (
                            cast_t("23:55") - cast_t("19:00") + 1 + cast_t("05:30"),
                            1,
                        ),
                        "text": "1 оператор + помощник",
                    },
                ],
            )
        )
        # make(make_meltings_1(schedule, LineName.SALT, 'Линия плавления моцареллы в рассоле №2'))
        make(
            make_meltings_2(
                master, LineName.SALT, "Линия плавления моцареллы в рассоле №2"
            )
        )
        make(
            make_shifts(
                0,
                [
                    {
                        "size": (cast_t("19:00") - cast_t("07:00"), 1),
                        "text": "Бригадир упаковки +5 рабочих упаковки + наладчик",
                    },
                    {
                        "size": (
                            cast_t("01:03:00") - cast_t("19:00") + 1 + cast_t("05:30"),
                            1,
                        ),
                        "text": "бригадир + наладчик + 5 рабочих",
                    },
                ],
            )
        )
        make(make_packings(master, LineName.SALT))
        make(make_extra_packings(extra_packings))

    return maker.root
