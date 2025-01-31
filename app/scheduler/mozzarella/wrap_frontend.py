from app.scheduler.rubber.to_boiling_plan import to_boiling_plan
from utils_ak.block_tree.block import Block
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push, simple_push
from utils_ak.block_tree.validation.class_validator import ClassValidator
from utils_ak.block_tree.validation.validate_disjoint import validate_disjoint
from utils_ak.builtin.collection import remove_neighbor_duplicates
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.numeric import custom_round

from app.enum import LineName
from app.scheduler.common.time_utils import cast_t, cast_time
from app.scheduler.common.wrap_header import wrap_header
from app.scheduler.mozzarella.make_schedule.make_schedule import make_schedule
from app.scheduler.rubber.wrap_frontend import wrap_frontend as wrap_frontend_rubber


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


def wrap_cheese_makers(master, rng, line_name: str):
    m = BlockMaker(
        "cheese_makers",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )

    for i, cheese_maker_num in enumerate(rng):
        with m.push(f"cheese_maker"):
            with m.push("header", push_func=add_push, index_width=0, start_time="00:00"):
                m.push(
                    "template",
                    push_func=add_push,
                    x=(1, 0),
                    size=(3, 2),
                    text=f"Сыроизготовитель №1 Poly {cheese_maker_num + 1}",
                    color=(183, 222, 232),
                )

            for boiling in master.iter(cls="boiling", pouring_line=str(cheese_maker_num)):
                boiling_model = boiling.props["boiling_model"]
                boiling_size = int(
                    round(
                        boiling_model.line.input_ton
                        * boiling.props.relative_props.get("boiling_volume", boiling_model.line.output_kg)
                        / boiling_model.line.output_kg
                    )
                )
                boiling_label = "{} {} {} {}кг".format(
                    boiling_model.percent,
                    boiling_model.ferment,
                    "" if boiling_model.is_lactose else "безлактозная",
                    boiling_size,
                )

                with m.push(
                    "pouring_block",
                    boiling_label=boiling_label,
                    boiling_id=boiling.props["boiling_id"],
                    x=(boiling["pouring"].x[0], 0),
                    push_func=add_push,
                    axis=1,
                ):
                    with m.push():
                        m.push_row("termizator", size=boiling["pouring"]["first"]["termizator"].size[0])
                        m.push_row(
                            "pouring_name",
                            size=boiling["pouring"].size[0] - boiling["pouring"]["first"]["termizator"].size[0],
                            boiling_label=boiling_label,
                        )
                    with m.push(font_size=8):
                        m.push_row(
                            "pouring_and_fermenting",
                            push_func=add_push,
                            size=boiling["pouring"]["first"]["termizator"].size[0]
                            + boiling["pouring"]["first"]["fermenting"].size[0],
                        )

                        m.push_row("soldification", size=boiling["pouring"]["first"]["soldification"].size[0])
                        m.push_row("cutting", size=boiling["pouring"]["first"]["cutting"].size[0])
                        m.push_row("pumping_out", size=boiling["pouring"]["first"]["pumping_out"].size[0])
                        m.push_row("pouring_off", size=boiling["pouring"]["second"]["pouring_off"].size[0])
                        m.push_row("extra", size=boiling["pouring"]["second"]["extra"].size[0])

        if i == 0:
            m.push(wrap_cleanings(master, line_name))
        else:
            m.push("stub", size=(0, 2))

    return m.root


def wrap_cleanings(master, line_name: str):
    m = BlockMaker(
        "cleanings_row",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )

    with m.push("header", push_func=add_push, index_width=0, start_time="00:00"):
        m.push(
            "template",
            push_func=add_push,
            x=(1, 0),
            size=(3, 2),
            text="Мойка термизатора",
            color="white",
            bold=True,
        )

    for cleaning in master.iter(cls="cleaning", line_name=line_name):
        b = m.copy(cleaning, with_props=True)
        b.update_size((b.props["size"][0], 2))
        m.push(b, push_func=add_push)

    return m.root


def wrap_multihead_cleanings(master):
    m = BlockMaker("multihead_cleanings_row", axis=1)
    for multihead_cleaning in master.iter(cls="multihead_cleaning"):
        b = m.copy(multihead_cleaning, with_props=True)
        b.update_size((b.props["size"][0], 1))
        m.push(b, push_func=add_push)
    return m.root


def wrap_meltings_1(master, line_name, title, coolings_mode="all"):
    m = BlockMaker(
        "melting",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )

    with m.push("header", push_func=add_push, start_time="00:00"):
        m.push(
            "template",
            index_width=0,
            x=(1, 0),
            size=(3, 2),
            text=title,
            push_func=add_push,
        )

    with m.push("melting_row", push_func=add_push):
        for boiling in master.iter(cls="boiling", boiling_model=lambda bm: bm.line.name == line_name):
            form_factor_label = calc_form_factor_label(
                [melting_process.props["bff"] for melting_process in boiling.iter(cls="melting_process")]
            )

            with m.push(
                "melting_block",
                push_func=add_push,
                axis=1,
                boiling_id=boiling.props["boiling_id"],
                form_factor_label=form_factor_label,
            ):
                with m.push("serving_row"):
                    m.push_row(
                        "serving",
                        push_func=add_push,
                        x=boiling["melting_and_packing"]["melting"]["serving"].x[0],
                        size=boiling["melting_and_packing"]["melting"]["serving"].size[0],
                    )

                with m.push("label_row"):
                    m.push_row(
                        "serving",
                        push_func=add_push,
                        x=boiling["melting_and_packing"]["melting"]["serving"].x[0],
                        size=boiling["melting_and_packing"]["melting"]["serving"].size[0],
                        visible=False,
                    )
                    m.push_row("melting_label", size=4)

                    assert (
                        boiling["melting_and_packing"]["melting"]["meltings"].size[0] >= 5
                    ), "В расписании есть блок плавления меньше 5 блоков. Такой случай не поддерживается. "

                    m.push_row(
                        "melting_name",
                        size=boiling["melting_and_packing"]["melting"]["meltings"].size[0] - 4,
                        form_factor_label=boiling.props["form_factor_label"],
                    )

                with m.push("melting_row"):
                    m.push_row(
                        "melting_process",
                        push_func=add_push,
                        x=boiling["melting_and_packing"]["melting"]["meltings"].x[0],
                        size=boiling["melting_and_packing"]["melting"]["meltings"].size[0],
                    )

    n_cooling_lines = 0
    m.push("cooling_row", axis=1)
    cooling_lines = []

    for boiling in master.iter(cls="boiling", boiling_model=lambda bm: bm.line.name == line_name):

        class Validator(ClassValidator):
            def __init__(self):
                super().__init__(window=10)

            @staticmethod
            def validate__cooling_block__cooling_block(b1, b2):
                validate_disjoint(b1, b2)

        cooling_label = "cooling" if line_name == LineName.WATER else "salting"

        cur_cooling_size = None
        for i, cooling_process in enumerate(
            boiling["melting_and_packing"]["melting"]["coolings"]["cooling_process", True]
        ):
            start_from = cooling_process["start"]["cooling", True][0].x[0]
            cooling_block = m.create_block("cooling_block", x=(start_from, 0))

            for cooling in cooling_process["start"]["cooling", True]:
                block = m.create_block(
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
                    new_cooling_line = m.create_block("cooling_line", size=(0, 1))
                    cooling_lines.append(new_cooling_line)
                    push(m.root["cooling_row"], new_cooling_line)

                res = simple_push(cooling_lines[j], cooling_block, validator=Validator())
                if isinstance(res, Block):
                    # pushed block successfully
                    break
                j += 1

                if n_cooling_lines == 100:
                    raise AssertionError("Создано слишком много линий охлаждения.")

    m.push("stub", size=(0, 2))
    return m.root


def wrap_shifts(shifts):
    m = BlockMaker("shifts")
    shifts = m.copy(shifts, with_props=True)
    for shift in shifts.iter(cls="shift"):
        shift.update_size(size=(shift.size[0], 1))  # todo maybe: refactor. Should be better [@marklidenberg]
    m.push(shifts, push_func=add_push)
    return m.root


def wrap_melting(boiling, line_name):
    m = BlockMaker("meltings", default_row_width=1, default_column_width=1, axis=1)

    form_factor_label = calc_form_factor_label(
        [melting_process.props["bff"] for melting_process in boiling.iter(cls="melting_process")]
    )
    cooling_label = "cooling" if line_name == LineName.WATER else "salting"

    with m.push(
        "melting_block",
        push_func=add_push,
        axis=1,
        boiling_id=boiling.props["boiling_id"],
        form_factor_label=form_factor_label,
    ):
        with m.push_row("label_row", push_func=add_push, x=boiling["melting_and_packing"]["melting"]["serving"].x[0]):
            m.push_row("melting_label", size=4, block_front_id=boiling.props["block_front_id"])
            assert (
                boiling["melting_and_packing"]["melting"].size[0] >= 5
            ), "В расписании есть блок плавления меньше 5 блоков. Такой случай пока не обработан. "
            m.push_row(
                "melting_name",
                size=boiling["melting_and_packing"]["melting"].size[0] - 4,
                form_factor_label=boiling.props["form_factor_label"],
            )

        with m.push("melting_row"):
            m.push_row(
                "serving",
                push_func=add_push,
                x=boiling["melting_and_packing"]["melting"]["serving"].x[0],
                size=boiling["melting_and_packing"]["melting"]["serving"].size[0],
            )

            m.push_row(
                "melting_process",
                push_func=add_push,
                x=(boiling["melting_and_packing"]["melting"]["meltings"].x[0], 0),
                size=(boiling["melting_and_packing"]["melting"]["meltings"].size[0], 1),
            )
            m.push_row(
                cooling_label,
                size=boiling["melting_and_packing"]["melting"]["coolings"]["cooling_process", True][-1]["start"].size[
                    0
                ],
            )

        with m.push("cooling_row"):
            m.push_row(
                cooling_label,
                push_func=add_push,
                x=boiling["melting_and_packing"]["melting"]["coolings"]["cooling_process", True][0]["start"].x[0],
                size=boiling["melting_and_packing"]["melting"]["coolings"]["cooling_process", True][0]["start"].size[0],
            )

    return m.root


def wrap_meltings_2(master, line_name, title):
    m = BlockMaker("melting", axis=1)

    n_lines = 5

    melting_lines = []
    for i in range(n_lines):
        melting_lines.append(m.push(f"salt_melting_{i}", size=(0, 3)).block)

        # add line for "Расход пара"
        m.push("stub", size=(0, 1))

    m.push(
        "template",
        push_func=add_push,
        index_width=0,
        x=(1, melting_lines[0].x[1]),
        size=(3, 6),
        start_time="00:00",
        text=title,
    )

    for i, boiling in enumerate(master.iter(cls="boiling", boiling_model=lambda bm: bm.line.name == line_name)):
        push(melting_lines[i % n_lines], wrap_melting(boiling, line_name), push_func=add_push)
    return m.root


def wrap_packing_block(packing_block, boiling_id):
    skus = [packing_process.props["sku"] for packing_process in packing_block.iter(cls="process")]
    group_form_factor_label = calc_group_form_factor_label(skus)
    brand_label = "/".join(remove_neighbor_duplicates([sku.brand_name for sku in skus]))
    m = BlockMaker(
        "packing_block",
        push_func=add_push,
        default_row_width=1,
        default_column_width=1,
        # props
        x=(packing_block.x[0], 0),
        boiling_id=boiling_id,
        axis=1,
        brand_label=brand_label,
        group_form_factor_label=group_form_factor_label,
    )
    with m.push():
        if packing_block.size[0] >= 4:
            m.push_row("packing_label", size=3)
            m.push_row("packing_name", size=packing_block.size[0] - 3)
        elif packing_block.size[0] >= 2:
            # update 2021.10.21
            m.push_row("packing_label", size=1)
            m.push_row("packing_name", size=packing_block.size[0] - 1)
        elif packing_block.size[0] == 1:
            # update 2021.10.21
            m.push_row("packing_label", size=1)

    with m.push():
        m.push_row("packing_brand", size=packing_block.size[0])

    with m.push():
        for packing_process in packing_block.iter(cls="process"):
            m.push_row(
                "packing_process", push_func=add_push, x=packing_process.props["x_rel"][0], size=packing_process.size[0]
            )
        for conf in packing_block.iter(cls="packing_configuration"):
            m.push_row("packing_configuration", push_func=add_push, x=conf.props["x_rel"][0], size=conf.size[0])
    return m.root


def wrap_packings(master, line_name):
    m = BlockMaker(
        "packing",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )

    for packing_team_id in range(1, 3):
        with m.push("packing_team", size=(0, 3), axis=0):
            for boiling in master.iter(cls="boiling", boiling_model=lambda bm: bm.line.name == line_name):
                for packing_block in boiling.iter(cls="collecting", packing_team_id=packing_team_id):
                    m.push(wrap_packing_block(packing_block, boiling.props["boiling_id"]), push_func=add_push)
            try:
                for conf in master["packing_configuration", True]:
                    # first level only
                    if conf.props["packing_team_id"] != packing_team_id or conf.props["line_name"] != line_name:
                        continue
                    m.push_row(
                        "packing_configuration", push_func=add_push, x=(conf.props["x"][0], 2), size=conf.size[0]
                    )
            except:
                # no packing_configuration in schedule first level
                pass
    return m.root


def wrap_extra_packings(extra_packings):
    m = BlockMaker("packing", axis=1)
    for packing_block in extra_packings.iter(cls="packing"):
        m.push(
            wrap_packing_block(packing_block, packing_block.props["boiling_id"]),
            push_func=add_push,
        )
    return m.root


def wrap_frontend(
    boiling_plan: str,
    coolings_mode="first",
    saturate=True,
    normalization=True,
    validate=True,
    first_batch_ids_by_type={"mozzarella": 1},
    rubber_start_time="07:00",
    # - Make basic_example schedule kwargs
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    optimize_cleanings=False,
    start_configuration=None,
    date=None,
):
    # - Get schedule first

    output = make_schedule(
        boiling_plan=boiling_plan,
        saturate=saturate,
        normalization=normalization,
        validate=validate,
        first_batch_ids_by_type=first_batch_ids_by_type,
        # - Make basic_example schedule kwargs
        date=date,
        optimize_cleanings=optimize_cleanings,
        start_times=start_times,
        start_configuration=start_configuration,
    )
    schedule = output["schedule"]

    # - Wrap frontend

    master = schedule["master"]
    extra_packings = schedule["extra_packings"]

    m = BlockMaker("root", axis=1)

    m.push("stub", size=(0, 1))

    start_t = min([boiling.x[0] for boiling in master["boiling", True]])  # first pouring time
    start_t = int(custom_round(start_t, 12, "floor"))  # round to last hour
    start_t -= 24
    start_time = cast_time(start_t)
    m.push(wrap_header(schedule.props["date"], start_time=start_time, header="График наливов"))
    with m.push("pouring", start_time=start_time, axis=1):
        if schedule["shifts"]:
            m.push(wrap_shifts(schedule["shifts"]["cheese_makers"]))
        m.push(wrap_cheese_makers(master, range(2), line_name=LineName.WATER))
        m.push("stub", size=(0, 2))
        m.push("stub", size=(0, 2))
        m.push(wrap_cheese_makers(master, range(2, 4), line_name=LineName.SALT))

    start_t = min([boiling["melting_and_packing"].x[0] for boiling in master["boiling", True]])  # first melting time
    start_t = int(custom_round(start_t, 12, "floor"))  # round to last hour
    start_t = min(start_t, cast_t(rubber_start_time))
    start_t -= 24
    start_time = cast_time(start_t)
    m.push(wrap_header(schedule.props["date"], start_time=start_time, header="График наливов"))

    with m.push("melting", start_time=start_time, axis=1):
        # - Check if water present

        is_water_present = (
            len(list(master.iter(cls="boiling", boiling_model=lambda bm: bm.line.name == LineName.WATER))) > 0
        )

        if is_water_present:
            # m.block(wrap_multihead_cleanings(master))
            if schedule["shifts"]:
                m.push(wrap_shifts(schedule["shifts"]["water_meltings"]))

            m.push(
                wrap_meltings_1(
                    master,
                    LineName.WATER,
                    "Линия плавления моцареллы в воде №1",
                    coolings_mode=coolings_mode,
                )
            )

            # make(make_meltings_2(schedule, LineName.WATER, 'Линия плавления моцареллы в воде №1'))
            if schedule["shifts"]:
                m.push(wrap_shifts(schedule["shifts"]["water_packings"]))

            m.push(wrap_packings(master, LineName.WATER))

        # - Process rubber

        rubber_boiling_plan_df = to_boiling_plan(boiling_plan)

        if not rubber_boiling_plan_df.empty and rubber_boiling_plan_df["kg"].sum() > 0:
            m.push_column("stub", size=1)
            m.push(wrap_frontend_rubber(boiling_plan=boiling_plan, start_time=rubber_start_time)["frontend"])
            m.push_column("stub", size=1)

        # - Process salt

        if schedule["shifts"]:
            m.push(wrap_shifts(schedule["shifts"]["salt_meltings"]))
        m.push(wrap_meltings_2(master, LineName.SALT, "Линия плавления моцареллы в рассоле №2"))
        if schedule["shifts"]:
            m.push(wrap_shifts(schedule["shifts"]["salt_packings"]))
        m.push(wrap_packings(master, LineName.SALT))
        m.push(wrap_extra_packings(extra_packings))

    # - Add frontend to output and return

    output["frontend"] = m.root

    return output


def test():
    print(
        wrap_frontend(
            """/Users/marklidenberg/Desktop/2024.04.19 терка мультиголовы/2024-03-08 План по варкам моцарелла.xlsx""",
            boiling_plan_rubber="""/Users/marklidenberg/Desktop/2024.04.19 терка мультиголовы/2024-03-08 План по варкам моцарелла.xlsx""",
        )
    )


if __name__ == "__main__":
    test()
