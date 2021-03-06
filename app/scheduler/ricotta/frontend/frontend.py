# fmt: off
from app.scheduler.time import *
from app.scheduler.frontend import *
from app.scheduler.header import wrap_header
from utils_ak.block_tree import *


def wrap_boiling(boiling):
    boiling_label = boiling.props["boiling_model"].short_display_name

    m = BlockMaker(
        "boiling",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        boiling_id=boiling.props["boiling_id"],
        boiling_label=boiling_label,
    )

    is_pumping_parallel = boiling["pumping_out"].x[0] < boiling["abandon"].y[0]

    with m.block("Upper line"):
        boiling_name_size = boiling.size[0] - boiling["heating"].size[0]

        if is_pumping_parallel:
            boiling_name_size -= boiling["pumping_out"].size[0]

        m.row("boiling_num", size=boiling["heating"].size[0])
        m.row("boiling_name", size=boiling_name_size)

        if is_pumping_parallel:
            m.row("pumping_out", size=boiling["pumping_out"].size[0])

    with m.block("Lower line"):
        m.row("heating", size=boiling["heating"].size[0], text="1900")
        m.row("delay", size=boiling["delay"].size[0])
        m.row("protein_harvest", size=boiling["protein_harvest"].size[0])
        m.row("abandon", size=boiling["abandon"].size[0])

        if not is_pumping_parallel:
            m.row("pumping_out", size=boiling["pumping_out"].size[0])

    with code('Steam consumption'):
        pass

        # deprecated (2021.06.04). Steam consumption is not needed anymore
        # with m.block():
        #     m.block(make_steam_blocks(boiling["steam_consumption"], x=(0, 0)))

    return m.root


def wrap_boiling_lines(schedule):
    m = BlockMaker(
        "boiling_lines",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )

    with code("init boiling lines"):
        boiling_lines = []
        n_lines = 3
        for i in range(n_lines):
            boiling_lines.append(m.block(f"boiling_line_{i}", size=(0, 3)).block)
            if i <= n_lines - 2:
                m.row("stub", size=0)

    with code("add boiling groups"):
        for boiling_group in schedule["boiling_group", True]:
            for i, line_num in enumerate(boiling_group.props["line_nums"]):
                boiling = boiling_group["boiling_sequence"]["boiling", True][i]
                push(
                    boiling_lines[line_num],
                    wrap_boiling(boiling),
                    push_func=add_push,
                )

    with code("add cleanings"):
        for i, cleaning in enumerate(schedule["bath_cleanings"]["bath_cleaning", True]):
            cleaning_block = m.copy(cleaning, with_props=True)
            for block in cleaning_block.children:
                block.update_size(size=(block.size[0], 2))
            push(boiling_lines[i], cleaning_block, push_func=add_push)

    return m.root


def wrap_analysis_line(schedule):
    m = BlockMaker(
        "analysis",
        default_row_width=1,
        default_col_width=1,
        # props
        size=(0, 2),
        axis=1,
    )

    class Validator(ClassValidator):
        def __init__(self):
            super().__init__(window=1)

        @staticmethod
        def validate__analysis_group__analysis_group(b1, b2):
            for c1 in b1.children:
                for c2 in b2.children:
                    validate_disjoint_by_axis(c1, c2)

    with code("init analysis lines"):
        n_lines = 2
        lines = []
        for i in range(n_lines):
            lines.append(m.row(f"analysis_line_{i}", size=0).block)

    for boiling_group in schedule["boiling_group", True]:
        analysis_group = m.create_block("analysis_group")
        for block in boiling_group["analysis_group"].children:
            _block = m.create_block(block.props["cls"],
                                    size=(block.size[0], 1),
                                    x=(block.x[0], 0))
            push(analysis_group, _block, push_func=add_push)

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


def wrap_packing_line(schedule):
    m = BlockMaker(
        "packing",
        default_row_width=1,
        default_col_width=1,
        # props
        size=(0, 1),
    )

    for boiling_group in schedule["boiling_group", True]:
        brand_label = calc_skus_label(boiling_group.props["skus"])

        m.row("packing_num", push_func=add_push,
              size=2,
              x=(boiling_group["packing"].x[0], 0),
              boiling_id=boiling_group.props["boiling_id"],
              font_size=9)

        m.row("packing", push_func=add_push,
              size=boiling_group["packing"].size[0] - 2,
              x=(boiling_group["packing"].x[0] + 2, 0),
              brand_label=brand_label,
              font_size=9)

    return m.root


def wrap_container_cleanings(schedule):
    m = BlockMaker(
        "container_cleanings",
        default_row_width=1,
        default_col_width=1,
        # props
        size=(0, 1),
    )

    for block in schedule["container_cleanings"].children:
        m.row(block.props["cls"], push_func=add_push,
              size=block.size[0],
              x=(block.x[0], 0))
    return m.root


def wrap_frontend(schedule, date=None):
    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1

    # calc start time
    start_t = int(utils.custom_round(schedule.x[0], 12, "floor"))  # round to last hour
    start_time = cast_time(start_t)

    m.block(wrap_header(date=date, start_time=start_time, header="График наливов сыворотки"))

    with m.block(start_time=start_time, axis=1):
        m.block(wrap_boiling_lines(schedule))
        m.block(wrap_analysis_line(schedule))
        m.block(wrap_packing_line(schedule))
        m.block(wrap_container_cleanings(schedule))
    return m.root
