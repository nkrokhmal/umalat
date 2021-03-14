from utils_ak.interactive_imports import *


def make_frontend_boiling(boiling):
    boiling_label = boiling.props["boiling_model"].short_display_name

    maker, make = init_block_maker(
        "boiling",
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        boiling_id=boiling.props["boiling_id"],
        boiling_label=boiling_label,
    )

    is_pumping_parallel = boiling["pumping_out"].x[0] < boiling["abandon"].y[0]

    with make():
        boiling_name_size = boiling.size[0] - boiling["heating"].size[0]

        if is_pumping_parallel:
            boiling_name_size -= boiling["pumping_out"].size[0]

        make("boiling_num", size=(boiling["heating"].size[0], 1))
        make("boiling_name", size=(boiling_name_size, 1))

        if is_pumping_parallel:
            make("pumping_out", size=(boiling["pumping_out"].size[0], 1))

    with make():
        make("heating", size=(boiling["heating"].size[0], 1), text="1900")
        make("delay", size=(boiling["delay"].size[0], 1))
        make("protein_harvest", size=(boiling["protein_harvest"].size[0], 1))
        make("abandon", size=(boiling["abandon"].size[0], 1))

        if not is_pumping_parallel:
            make("pumping_out", size=(boiling["pumping_out"].size[0], 1))
    with make(font_size=8):
        sc = boiling["steam_consumption"]
        for j in range(sc.size[0]):
            make(
                x=(j, 0),
                size=(1, 1),
                text=str(sc.props["value"]),
                text_rotation=90,
                push_func=add_push,
                # border=None,
            )
    return maker.root


def make_boiling_lines(schedule):
    maker, make = init_block_maker("boiling_lines", axis=1)

    boiling_lines = []
    for i in range(3):
        boiling_lines.append(
            make(f"boiling_line_{i}", size=(0, 3), is_parent_node=True).block
        )
        if i <= 1:
            make("stub", size=(0, 1))

    for boiling_group in listify(schedule["boiling_group"]):
        for i, line_num in enumerate(boiling_group.props["line_nums"]):
            boiling = listify(boiling_group["boiling_sequence"]["boiling"])[i]
            push(
                boiling_lines[line_num],
                make_frontend_boiling(boiling),
                push_func=add_push,
            )

    for i, cleaning in enumerate(listify(schedule["bath_cleanings"]["bath_cleaning"])):
        cleaning_block = maker.copy(cleaning, with_props=True)
        for block in cleaning_block.children:
            block.props.update(size=(block.size[0], 2))
        push(boiling_lines[i], cleaning_block, push_func=add_push)

    return maker.root


def make_analysis_line(schedule):
    maker, make = init_block_maker("analysis", size=(0, 1), is_parent_node=True)

    for boiling_group in listify(schedule["boiling_group"]):
        with make("analysis_group", push_func=add_push):
            for block in boiling_group["analysis_group"].children:
                make(
                    block.props["cls"],
                    size=(block.size[0], 1),
                    x=(block.x[0], 0),
                    push_func=add_push,
                )
    return maker.root


def calc_skus_label(skus):
    values = []
    for sku in skus:
        values.append([sku.brand_name, str(sku.weight_netto)])

    tree = df_to_ordered_tree(pd.DataFrame(values))

    return "/".join(
        [
            group_label + " " + "/".join(form_factor_labels)
            for group_label, form_factor_labels in tree
        ]
    )


def make_packing_line(schedule):
    maker, make = init_block_maker("packing", size=(0, 1), is_parent_node=True)

    for boiling_group in listify(schedule["boiling_group"]):
        brand_label = calc_skus_label(boiling_group.props["skus"])

        make(
            "packing_num",
            size=(2, 1),
            x=(boiling_group["packing"].x[0], 0),
            push_func=add_push,
            boiling_id=boiling_group.props["boiling_id"],
        )

        make(
            "packing",
            size=(boiling_group["packing"].size[0] - 2, 1),
            x=(boiling_group["packing"].x[0] + 2, 0),
            push_func=add_push,
            brand_label=brand_label,
        )

    return maker.root


def make_container_cleanings(schedule):
    maker, make = init_block_maker(
        "container_cleanings", size=(0, 1), is_parent_node=True
    )

    for block in schedule["container_cleanings"].children:
        make(
            block.props["cls"],
            size=(block.size[0], 1),
            x=(block.x[0], 0),
            push_func=add_push,
        )
    return maker.root


def make_frontend(schedule):
    maker, make = init_block_maker("frontend", axis=1)
    make("stub", size=(0, 1))  # start with 1
    make(make_boiling_lines(schedule))
    make(make_analysis_line(schedule))
    make(make_packing_line(schedule))
    make(make_container_cleanings(schedule))
    return maker.root
