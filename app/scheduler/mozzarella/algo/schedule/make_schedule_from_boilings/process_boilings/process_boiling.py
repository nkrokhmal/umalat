from app.imports.runtime import *
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.make_termizator_cleaning_block import (
    make_termizator_cleaning_block,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.validator import Validator

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.scheduler.shifts import *
from app.enum import LineName

from app.scheduler.mozzarella.algo.schedule.custom_pushers import *
from utils_ak.block_tree import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def process_boiling(
    m: BlockMaker,  # SIDE EFFECTS, will be changed
    boiling: ParallelepipedBlock,
    last_multihead_water_boiling: ParallelepipedBlock,
    lines_df: pd.DataFrame,
    cleaning_type_by_boiling_id: dict,
    shrink_drenators: bool = True,
    strict_order: bool = False,
) -> BlockMaker:

    # - Extract line name

    line_name = boiling.props["boiling_model"].line.name

    # - Find start_from

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

    # - Add configuration if needed

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
                m.root["master"],
                conf,
                push_func=AxisPusher(start_from="beg"),
                validator=Validator(),
            )

    # - Filter iter_props: no two boilings allowed sequentially on the same pouring line

    iter_props = lines_df.at[line_name, "iter_props"]
    if lines_df.at[line_name, "latest_boiling"]:
        current_pouring_line = lines_df.at[line_name, "latest_boiling"].props["pouring_line"]
        iter_props = [props for props in iter_props if props["pouring_line"] != current_pouring_line]

    # - Push boiling

    push(
        m.root["master"],
        boiling,
        push_func=AxisPusher(start_from=start_from),
        iter_props=iter_props,
        validator=Validator(strict_order=strict_order),
        max_tries=100,
    )

    # - Fix water a little bit: try to push water before - allowing awaiting in line

    if line_name == LineName.WATER and lines_df.at[LineName.WATER, "latest_boiling"]:
        boiling.detach_from_parent()
        push(
            m.root["master"],
            boiling,
            push_func=AwaitingPusher(max_period=8),
            validator=Validator(strict_order=strict_order),
            max_tries=9,
        )

    # - Fix water a little bit: try to shrink drenator a little bit for compactness

    if shrink_drenators:

        if lines_df.at[LineName.WATER, "latest_boiling"]:
            boiling.detach_from_parent()
            push(
                m.root["master"],
                boiling,
                push_func=DrenatorShrinkingPusher(max_period=-2),
                validator=Validator(strict_order=strict_order),
                max_tries=3,
            )

    # - Move rubber packing to extras

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
        packing.props.update(deactivated=True)  # used in make_configuration_blocks function
        push(m.root["extra"], packing_copy, push_func=add_push)

    # - Add multihead boiling after all water boilings if multihead was present

    if boiling == last_multihead_water_boiling:
        push(
            m.root["master"],
            m.create_block(
                "multihead_cleaning",
                x=(boiling.y[0], 0),
                size=(cast_t("03:00"), 0),
            ),
            push_func=add_push,
        )
        push(
            m.root["extra"],
            m.create_block(
                "multihead_cleaning",
                x=(boiling.y[0], 0),
                size=(cast_t("03:00"), 0),
            ),
            push_func=add_push,
        )

    # - Add cleaning after boiling if needed

    cleaning_type = cleaning_type_by_boiling_id.get(boiling.props["boiling_id"])
    if cleaning_type:
        start_from = boiling["pouring"]["first"]["termizator"].y[0]
        cleaning = make_termizator_cleaning_block(
            cleaning_type,
            x=(boiling["pouring"]["first"]["termizator"].y[0], 0),
            rule="manual",
        )
        push(
            m.root["master"],
            cleaning,
            push_func=AxisPusher(start_from=start_from),
            validator=Validator(),
        )

    # - Set latest boiling

    lines_df.at[line_name, "latest_boiling"] = boiling

    # - Return

    return m
