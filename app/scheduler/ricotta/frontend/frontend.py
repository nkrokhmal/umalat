from app.scheduler.time import *
from app.scheduler.frontend import *

from utils_ak.block_tree import *


def make_frontend_boiling(boiling):
    boiling_label = boiling.props["boiling_model"].short_display_name

    m = BlockMaker(
        "boiling",
        default_row_width=1,
        default_col_width=1,
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        boiling_id=boiling.props["boiling_id"],
        boiling_label=boiling_label,
    )

    is_pumping_parallel = boiling["pumping_out"].x[0] < boiling["abandon"].y[0]

    with m.block():
        boiling_name_size = boiling.size[0] - boiling["heating"].size[0]

        if is_pumping_parallel:
            boiling_name_size -= boiling["pumping_out"].size[0]

        m.row("boiling_num", size=boiling["heating"].size[0])
        m.row("boiling_name", size=boiling_name_size)

        if is_pumping_parallel:
            m.row("pumping_out", size=boiling["pumping_out"].size[0])

    with m.block():
        m.row("heating", size=boiling["heating"].size[0], text="1900")
        m.row("delay", size=boiling["delay"].size[0])
        m.row("protein_harvest", size=boiling["protein_harvest"].size[0])
        m.row("abandon", size=boiling["abandon"].size[0])

        if not is_pumping_parallel:
            m.row("pumping_out", size=boiling["pumping_out"].size[0])

    with m.block():
        m.block(make_steam_blocks(boiling["steam_consumption"], x=(0, 0)))

    return m.root


def make_boiling_lines(schedule):
    m = BlockMaker("boiling_lines", default_row_width=1, default_col_width=1, axis=1)

    boiling_lines = []
    for i in range(3):
        boiling_lines.append(
            m.block(f"boiling_line_{i}", size=(0, 3), is_parent_node=True).block
        )
        if i <= 1:
            m.row("stub", size=0)

    for boiling_group in schedule["boiling_group", True]:
        for i, line_num in enumerate(boiling_group.props["line_nums"]):
            boiling = boiling_group["boiling_sequence"]["boiling", True][i]
            push(
                boiling_lines[line_num],
                make_frontend_boiling(boiling),
                push_func=add_push,
            )

    for i, cleaning in enumerate(schedule["bath_cleanings"]["bath_cleaning", True]):
        cleaning_block = m.copy(cleaning, with_props=True)
        for block in cleaning_block.children:
            block.props.update(size=(block.size[0], 2))
        push(boiling_lines[i], cleaning_block, push_func=add_push)

    return m.root


def make_analysis_line(schedule):
    m = BlockMaker("analysis", size=(0, 2), axis=1, is_parent_node=True)

    class Validator(ClassValidator):
        def __init__(self):
            super().__init__(window=1)

        @staticmethod
        def validate__analysis_group__analysis_group(b1, b2):
            for c1 in b1.children:
                for c2 in b2.children:
                    validate_disjoint_by_axis(c1, c2)

    n_lines = 2

    lines = []
    for i in range(n_lines):
        lines.append(
            m.block(f"analysis_line_{i}", size=(0, 1), is_parent_node=False).block
        )

    # todo: hardcode
    for line in lines:
        push(line, m.create_block("stub", size=(0, 1)), push_func=add_push)

    for boiling_group in schedule["boiling_group", True]:
        analysis_group = m.create_block("analysis_group")
        for block in boiling_group["analysis_group"].children:
            _block = m.create_block(
                block.props["cls"],
                size=(block.size[0], 1),
                x=(block.x[0], 0),
            )
            push(analysis_group, _block, push_func=add_push)
        # todo: refactor
        for i, line in enumerate(lines):
            res = push(
                line,
                analysis_group,
                push_func=lambda parent, block: simple_push(
                    parent, block, validator=Validator()
                ),
            )
            if not isinstance(res, dict):
                # success
                break
            else:
                if i == len(lines) - 1:
                    # last one
                    raise Exception(
                        "Не получилось прорисовать баки Ришад-Ричи на двух линиях."
                    )
    return m.root


def calc_skus_label(skus):
    values = []
    for sku in skus:
        values.append([str(sku.weight_netto), sku.brand_name])

    tree = utils.df_to_ordered_tree(pd.DataFrame(values))
    return ", ".join(
        [
            "/".join(form_factor_labels) + " " + group_label
            for group_label, form_factor_labels in tree
        ]
    )


def make_packing_line(schedule):
    m = BlockMaker("packing", size=(0, 1), is_parent_node=True)

    for boiling_group in schedule["boiling_group", True]:
        brand_label = calc_skus_label(boiling_group.props["skus"])

        m.block(
            "packing_num",
            size=(2, 1),
            x=(boiling_group["packing"].x[0], 0),
            push_func=add_push,
            boiling_id=boiling_group.props["boiling_id"],
            font_size=9,
        )

        m.block(
            "packing",
            size=(boiling_group["packing"].size[0] - 2, 1),
            x=(boiling_group["packing"].x[0] + 2, 0),
            push_func=add_push,
            brand_label=brand_label,
            font_size=9,
        )

    return m.root


def make_container_cleanings(schedule):
    m = BlockMaker("container_cleanings", size=(0, 1), is_parent_node=True)

    for block in schedule["container_cleanings"].children:
        m.block(
            block.props["cls"],
            size=(block.size[0], 1),
            x=(block.x[0], 0),
            push_func=add_push,
        )
    return m.root


def make_header(date, start_time="07:00"):
    m = BlockMaker("header", axis=1)

    with m.block("header", size=(0, 1), index_width=2):
        m.block(size=(1, 1), text="График наливов сыворотки")
        m.block(size=(1, 1), text=utils.cast_str(date, "%d.%m.%Y"), bold=True)
        for i in range(566):
            cur_time = cast_time(i + cast_t(start_time))
            days, hours, minutes = cur_time.split(":")
            if cur_time[-2:] == "00":
                m.block(
                    size=(1, 1),
                    text=str(int(hours)),
                    color=(218, 150, 148),
                    text_rotation=90,
                    font_size=9,
                )
            else:
                m.block(
                    size=(1, 1),
                    text=minutes,
                    color=(204, 255, 255),
                    text_rotation=90,
                    font_size=9,
                )
    return m.root["header"]


def make_frontend(schedule, date=None, start_time="07:00"):
    date = date or datetime.now()

    m = BlockMaker("frontend", axis=1)
    m.block("stub", size=(0, 1))  # start with 1
    m.block(make_header(date=date, start_time=start_time))
    m.block(make_boiling_lines(schedule))
    m.block(make_analysis_line(schedule))
    m.block(make_packing_line(schedule))
    m.block(make_container_cleanings(schedule))
    return m.root
