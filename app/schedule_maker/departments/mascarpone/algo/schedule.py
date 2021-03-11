from utils_ak.block_tree import *

from app.schedule_maker.models import *

validator = ClassValidator(window=3)


def validate(b1, b2):
    pass


validator.add("boiling_group", "boiling_group", validate)


def make_schedule(boiling_plan_df):
    maker, make = init_block_maker("schedule")

    boiling_groups = []
    for boiling_id, grp in boiling_plan_df.groupby("boiling_id"):
        boiling_groups.append(make_boiling_group(grp))

    prev_line_nums = None
    for bg_prev, bg in SimpleIterator(boiling_groups).iter_sequences(2, method="any"):
        if not bg:
            # last iteration
            continue

        n_boilings = len(listify(bg["boiling_sequence"]["boiling"]))

        line_nums_props = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
        idx = 0
        if bg_prev:
            idx = bg_prev.props["line_nums"][-1]  # ended with number
            idx = (idx + 1) % len(line_nums_props)  # next line_nums in circle
        bg.props.update(line_nums=line_nums_props[idx][:n_boilings])

        push(
            maker.root,
            bg,
            push_func=AxisPusher(start_from="last_beg"),
            validator=validator,
        )

    # add bat cleanings
    bath_cleanings = make_bath_cleanings()
    push(
        maker.root,
        bath_cleanings,
        push_func=AxisPusher(start_from="last_beg"),
        validator=validator,
    )

    # add container cleanings
    container_cleanings = make_container_cleanings()

    push(
        maker.root,
        container_cleanings,
        push_func=AxisPusher(start_from=boiling_groups[-1]["analysis_group"].x[0]),
        validator=validator,
    )

    return maker.root
