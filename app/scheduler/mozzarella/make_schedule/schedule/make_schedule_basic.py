import itertools
import warnings

from datetime import datetime
from typing import Literal, Optional

import numpy as np
import pandas as pd

from loguru import logger
from utils_ak.block_tree import ParallelepipedBlock
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.block_tree.validation.class_validator import ClassValidator
from utils_ak.block_tree.validation.validate_disjoint import validate_disjoint
from utils_ak.block_tree.validation.validate_order_by_axis import validate_order_by_axis
from utils_ak.builtin.collection import delistify
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.iteration.simple_iterator import iter_pairs

from app.enum import LineName
from app.models import Washer, cast_model
from app.scheduler.common.split_shifts_utils import split_shifts
from app.scheduler.common.time_utils import cast_t, cast_time
from app.scheduler.mozzarella.make_schedule.packing import boiling_has_multihead_packing, make_configuration_blocks
from app.scheduler.mozzarella.make_schedule.schedule.calc_partial_score import calc_partial_score
from app.scheduler.mozzarella.make_schedule.schedule.make_boilings import make_boilings
from app.scheduler.mozzarella.make_schedule.schedule.pushers.awaiting_pusher import AwaitingPusher
from app.scheduler.mozzarella.make_schedule.schedule.pushers.backwards_pusher import BackwardsPusher
from app.scheduler.mozzarella.make_schedule.schedule.pushers.drenator_shrinking_pusher import DrenatorShrinkingPusher
from app.scheduler.mozzarella.make_schedule.schedule.run_in_parallel import run_in_parallel
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan


BLOCKS = []

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


MAX_SCORE = 10000000000


class Validator(ClassValidator):
    def __init__(
        self,
        window=100,
        strict_order: Literal["none", "all", "same_line"] = "none",
        water_melting_overlap_limit: Optional[int] = None,
    ):
        # NOTE: we have window 100 - so we basically check every combination of boilings with each other. It was easier to do this way, just brute validation
        super().__init__(window=window)
        self.strict_order = strict_order
        self.water_melting_overlap_limit = water_melting_overlap_limit

    def validate__boiling__boiling(self, b1, b2):
        # - Sort by x

        if b1.x[0] == b2.x[0]:
            b1s, b2s = b1, b2
        else:
            b1s, b2s = (
                min([b1, b2], key=lambda b: b.x[0]),
                max([b1, b2], key=lambda b: b.x[0]),
            )

        # - Define line names (water/salt) that we work on (which corresponds to the pouring line)

        wln1 = LineName.WATER if b1s["pouring"].props["pouring_line"] in ["0", "1"] else LineName.SALT
        wln2 = LineName.WATER if b2s["pouring"].props["pouring_line"] in ["0", "1"] else LineName.SALT

        # - Extract boiling models

        boiling_model1 = b1s.props["boiling_model"]
        boiling_model2 = b2s.props["boiling_model"]

        # - Early exit if the salt is on the 3 line

        if b1s.props["boiling_model"].line.name != b2s.props["boiling_model"].line.name and wln1 == wln2:
            validate_disjoint(
                b1s["pouring"]["first"]["termizator"],
                b2s["pouring"]["first"]["termizator"],
                ordered=True,
            )

        # - Early exit if on the same pouring line - strict termizator

        if b1s["pouring"].props["pouring_line"] == b2s["pouring"].props["pouring_line"]:
            validate_disjoint(
                b1s["pouring"]["first"]["termizator"],
                b2s["pouring"]["first"]["termizator"],
                ordered=True,
            )

        # - Basic validations

        if b1s.props["boiling_model"].line.name == b2s.props["boiling_model"].line.name:
            validate_disjoint(b1s["pouring"]["first"]["termizator"], b2s["pouring"]["first"]["termizator"])
            validate_disjoint(b1s["pouring"]["second"]["pouring_off"], b2s["pouring"]["second"]["pouring_off"])
            validate_disjoint(b1s["pouring"]["first"]["pumping_out"], b2s["pouring"]["second"]["pouring_off"])
            validate_disjoint(b1s["pouring"]["second"]["pouring_off"], b2s["pouring"]["first"]["pumping_out"])

        # - Process boilings on the same pouring line

        if b1s["pouring"].props["pouring_line"] == b2s["pouring"].props["pouring_line"]:
            # pourings should not intersect, but also five minutes should be between boilings
            validate_disjoint(b1s["pouring"], b2s["pouring"], ordered=True)

            # if boilings use same drenator - drenator should not intersect with meltings
            if b1s.props["drenator_num"] == b2s.props["drenator_num"]:
                validate_disjoint(b1s["melting_and_packing"]["melting"]["meltings"], b2s["drenator"])

        # - Process lines

        if boiling_model1.line.name == boiling_model2.line.name:
            # same lines

            # - Meltings with meltings, collecting with collecting

            validate_disjoint(
                b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["meltings"]
            )
            for p1, p2 in itertools.product(
                b1s["melting_and_packing"]["collecting", True], b2s["melting_and_packing"]["collecting", True]
            ):
                validate_disjoint(p1, p2)

            # - Process lactose to non-lactose and vice versa

            # if water and different boilings - cannot intersect serving with meltings
            if boiling_model1 != boiling_model2:
                if not boiling_model1.is_lactose and boiling_model2.is_lactose:
                    # - Check if first non-lactose boiling is full

                    _df = b1s.props["boiling_group_df"]
                    _df["is_lactose"] = _df["sku"].apply(lambda sku: sku.made_from_boilings[0].is_lactose)
                    _is_full = not _df["is_lactose"].any()

                    validate_disjoint(
                        b1s["melting_and_packing"]["melting"]["meltings"],
                        b2s["melting_and_packing"]["melting"]["serving"],
                        distance=-2 if _is_full else -6,  # 10 минут, если полная и 30м, если неполная
                        ordered=True,
                    )
                elif boiling_model1.is_lactose and not boiling_model2.is_lactose:
                    validate_disjoint(
                        b1s["melting_and_packing"]["melting"]["meltings"],
                        b2s["melting_and_packing"]["melting"]["serving"],
                        distance=2,
                        ordered=True,
                    )

            # - Process water melting overlap

            if self.water_melting_overlap_limit:
                validate_disjoint(
                    b1s["melting_and_packing"]["melting"]["meltings"],
                    b2s["melting_and_packing"]["melting"]["serving"],
                    distance=self.water_melting_overlap_limit,
                    ordered=True,
                )
        else:
            # different lines

            if wln1 == wln2:
                # same working lines (means that salt and water on the same working line - due to salt switching to the first pouring_line)

                # basic_example validations
                validate_disjoint(
                    b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["meltings"]
                )
                validate_disjoint(
                    b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"]
                )

                _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
                _b2s = b2s["melting_and_packing"]["melting"]["meltings"]

                validate_disjoint(_b1s, _b2s, distance=7, ordered=True)

        # - Validate strict order

        if (
            self.strict_order == "all"
            or self.strict_order == "same_line"
            and b1.props["boiling_model"].line.name == b2.props["boiling_model"].line.name
        ):
            validate_order_by_axis(b1, b2)

    def validate__cleaning__cleaning(self, b1, b2):
        if b1.props["line_name"] == b2.props["line_name"]:
            validate_disjoint(b1, b2)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        if b1.props["boiling_model"].line.name != b2.props["line_name"]:
            return

        boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        validate_disjoint(boiling["pouring"]["first"]["termizator"], cleaning)

    @staticmethod
    def validate__cleaning__boiling(b1, b2):
        if b1.props["line_name"] != b2.props["boiling_model"].line.name:
            return

        boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        validate_disjoint(cleaning, boiling["pouring"]["first"]["termizator"])

    @staticmethod
    def validate__boiling__packing_configuration(b1, b2):
        boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        if boiling.props["boiling_model"].line.name != packing_configuration.props["line_name"]:
            return

        for p1 in boiling.iter(cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]):
            validate_disjoint(p1, b2)

    @staticmethod
    def validate__packing_configuration__boiling(b1, b2):
        boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        if boiling.props["boiling_model"].line.name != packing_configuration.props["line_name"]:
            return

        for p1 in boiling.iter(cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]):
            validate_disjoint(b1, p1)


def make_termizator_cleaning_block(cleaning_type, **kwargs):
    washer = cast_model(
        Washer,
        "Короткая мойка термизатора" if cleaning_type == "short" else "Длинная мойка термизатора",
    )
    m = BlockMaker(
        "cleaning",
        size=(washer.time // 5, 0),
        cleaning_type=cleaning_type,
        **kwargs,
    )
    return m.root


class ScheduleMaker:
    def _init_block_maker(self):
        self.m = BlockMaker("schedule")
        self.m.root.props.update(date=self.date)
        self.m.push("master")
        self.m.push("extra")
        self.m.push("extra_packings")

        with self.m.push("shifts"):
            self.m.push("cheese_makers")
            self.m.push("water_meltings")
            self.m.push("water_packings")
            self.m.push("salt_meltings")
            self.m.push("salt_packings")

    def _init_lines_df(self):
        # init lines df
        lines_df = pd.DataFrame(
            index=[LineName.WATER, LineName.SALT],
            columns=["iter_props", "start_time", "boilings_left"],
        )

        # init iter_props
        lines_df.at[LineName.WATER, "iter_props"] = [
            {"pouring_line": str(v1), "drenator_num": str(v2)} for v1, v2 in itertools.product([0, 1], [0, 1, 2, 3])
        ]
        lines_df.at[LineName.SALT, "iter_props"] = [
            {"pouring_line": str(v1), "drenator_num": str(v2)} for v1, v2 in itertools.product([2, 3], [4, 5, 6, 7])
        ]

        self.lines_df = lines_df

    def _init_left_df(self):
        # make left_df
        values = [
            [
                boiling,
                boiling.props["boiling_model"].line.name,
                boiling.props["sheet"],
            ]
            for boiling in self.boilings
        ]
        left_df = (
            pd.DataFrame(values, columns=["boiling", "line_name", "sheet"])
            .reset_index()
            .sort_values(by=["sheet", "index"])
        )

        self.left_df = left_df

        # check for empty input
        assert (
            len(left_df) > 0
        ), "На вход не подано ни одной варки. Укажите хотя бы одну варку для составления расписания."

    def _init_multihead_water_boilings(self):
        # init water boilings using multihead
        self.multihead_water_boilings = [
            row["boiling"]
            for i, row in self.left_df.iterrows()
            if boiling_has_multihead_packing(row["boiling"])
            and row["boiling"].props["boiling_model"].line.name == LineName.WATER
        ]

        # init last multihead boiling
        if self.multihead_water_boilings:
            self.last_multihead_water_boiling = self.multihead_water_boilings[-1]
        else:
            self.last_multihead_water_boiling = None

    def _process_boiling(self, boiling, shrink_drenators: bool = True, tag: str = ""):
        # - Extract line name

        line_name = boiling.props["boiling_model"].line.name

        # - Find start_from

        if latest_boiling := self.get_latest_boiling(line_name=boiling.props["boiling_model"].line.name):
            # start from latest boiling
            start_from = latest_boiling.x[0] - self.m.root.x[0]  # remove root offset
        else:
            start_from = (
                cast_t(self.start_times[boiling.props["boiling_model"].line.name]) - boiling["melting_and_packing"].x[0]
            )

        # - Add configuration if needed

        if self.get_latest_boiling(line_name):
            configuration_blocks = make_configuration_blocks(
                self.get_latest_boiling(line_name),
                boiling,
                self.m,
                line_name,
                between_boilings=True,
            )
            for block in configuration_blocks:
                # SIDE EFFECT
                block.props.update(tag=tag, line_name=line_name)

                # print("Pushing", block.props['cls'])
                push(
                    self.m.root["master"],
                    block,
                    push_func=AxisPusher(start_from="beg"),
                    validator=Validator(),
                )

        # - Filter iter_props: no two boilings allowed sequentially on the same pouring line

        iter_props = self.lines_df.at[line_name, "iter_props"]
        if self.get_latest_boiling(line_name):
            current_pouring_line = self.get_latest_boiling(line_name).props["pouring_line"]
            iter_props = [props for props in iter_props if props["pouring_line"] != current_pouring_line]

        # - Push boiling

        # SIDE EFFECT
        boiling.props.update(tag_boiling=tag)
        # print("Pushing", boiling.props['cls'])

        push(
            self.m.root["master"],
            boiling,
            push_func=AxisPusher(start_from=start_from),
            iter_props=iter_props,
            validator=Validator(strict_order="same_line"),
            max_tries=100,
        )

        # - Fix water a little bit: try to push water before - allowing awaiting in line

        if line_name == LineName.WATER and boiling != self.get_earliest_boiling(line_name):
            # - Get current boiling serving start

            boiling_serving_start_t = cast_t(boiling["melting_and_packing"]["melting"]["serving"].x[0])

            # - Detach from the parent

            boiling.detach_from_parent()

            # - Get latest melting end

            current_melting_end_t = cast_t(
                self.get_latest_boiling(line_name)["melting_and_packing"]["melting"]["meltings"].y[0]
            )

            # - Push

            push(
                self.m.root["master"],
                boiling,
                push_func=AwaitingPusher(max_period=24),
                validator=Validator(
                    strict_order="same_line",
                    water_melting_overlap_limit=min(
                        -2, boiling_serving_start_t - current_melting_end_t
                    ),  # when optimizing - max 10 minutes overlap is allowed (but if already more - keep it)
                ),
                max_tries=25,
            )

        # # - Shrink drenators
        # DEPRECATED (2024-12-18): became irrelevant after we got the second termizator. This optimization aims to make pouring earlier, it's not needed anymore
        # if shrink_drenators:
        #     # fix water a little bit: try to shrink drenator a little bit for compactness
        #     if self.get_latest_boiling(LineName.WATER):
        #         # SIDE EFFECT
        #         boiling.detach_from_parent()
        #         push(
        #             self.m.root["master"],
        #             boiling,
        #             push_func=DrenatorShrinkingPusher(max_period=-2),
        #             validator=Validator(strict_order="same_line"),
        #             max_tries=3,
        #         )

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

            packing_copy = self.m.copy(packing, with_props=True)
            packing_copy.props.update(extra_props={"start_from": packing.x[0]})
            packing.props.update(deactivated=True)  # used in make_configuration_blocks function

            # SIDE EFFECT
            # print("Pushing", packing_copy.props['cls'])
            packing_copy.props.update(tag=tag)
            push(self.m.root["extra"], packing_copy, push_func=add_push)

        # - Add multihead boiling after all water boilings if multihead was present

        if boiling == self.last_multihead_water_boiling:
            # SIDE EFFECT
            # print("Pushing", 'multihead_cleaning')

            push(
                self.m.root["master"],
                self.m.create_block(
                    "multihead_cleaning",
                    x=(boiling.y[0], 0),
                    size=(cast_t("03:00"), 0),
                    tag=tag,
                ),
                push_func=add_push,
            )
            push(
                self.m.root["extra"],
                self.m.create_block(
                    "multihead_cleaning",
                    x=(boiling.y[0], 0),
                    size=(cast_t("03:00"), 0),
                    tag=tag,
                ),
                push_func=add_push,
            )

        # - Add cleaning after boiling if needed

        if cleaning_type := self.cleanings.get(boiling.props["group_id"]):
            push(
                self.m.root["master"],
                make_termizator_cleaning_block(
                    cleaning_type,
                    x=(boiling["pouring"]["first"]["termizator"].y[0], 0),
                    rule="manual",
                    line_name=boiling.props["boiling_model"].line.name,
                    tag=tag,
                ),
                push_func=AxisPusher(start_from=boiling["pouring"]["first"]["termizator"].y[0]),
                validator=Validator(),
            )

        # - Check if only salt left -> start working on 3 (third) line

        if (self.left_df["line_name"] == LineName.SALT).all():
            logger.info("Only salt left, working on the third line")
            self.lines_df.at[LineName.SALT, "iter_props"] = [
                {"pouring_line": str(v1), "drenator_num": str(v2)}
                for v1, v2 in itertools.product([2, 3, 1], [4, 5, 6, 7])
            ]

        # - Return

        return boiling

    def _process_boilings(self):
        # - Configuration is water first, then salt

        """
        NOTE: before the production had only one termizator, we had to find the optimal configuration of water and salt boilings.
        Now they are independent - so we first do the water and then the salt
        """

        configuration = [LineName.WATER] * len(self.left_df[self.left_df["line_name"] == LineName.WATER]) + [
            LineName.SALT
        ] * len(self.left_df[self.left_df["line_name"] == LineName.SALT])

        logger.info("Configuration", configuration=configuration)

        # - Process configuration

        for i, line_name in enumerate(configuration):
            # - Select next row

            next_row = self.left_df[self.left_df["line_name"] == line_name].iloc[0]

            # for debug for easier navigation
            # next_row["boiling"].props.update(boiling_id=i + 1)

            # remove newly added row from left rows
            self.left_df = self.left_df[self.left_df["index"] != next_row["index"]]

            self._process_boiling(
                next_row["boiling"],
                shrink_drenators=False,
            )

    def get_earliest_boiling(self, line_name: Optional[str] = None):
        boilings = self.m.root["master"]["boiling", True]

        if line_name is not None:
            boilings = [b for b in boilings if b.props["boiling_model"].line.name == line_name]

        if not boilings:
            return None

        return boilings[0]

    def get_latest_boiling(self, line_name: Optional[str] = None):
        boilings = self.m.root["master"]["boiling", True]

        if line_name is not None:
            boilings = [b for b in boilings if b.props["boiling_model"].line.name == line_name]

        if not boilings:
            return None

        return boilings[-1]

    def get_latest_boilings(self):
        result = [self.get_latest_boiling(line_name) for line_name in [LineName.WATER, LineName.SALT]]
        result = [b for b in result if b is not None]
        return result

    def _process_extras(self):
        # push extra packings
        class ExtraValidator(ClassValidator):
            def __init__(self):
                super().__init__(window=10)

            @staticmethod
            def validate__packing__packing(b1, b2):
                return validate_disjoint(b1, b2)

            @staticmethod
            def validate__multihead_cleaning__packing(b1, b2):
                multihead_cleaning, packing = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
                for process in packing.iter(cls="process"):
                    packer = delistify(process.props["sku"].packers, single=True)
                    if packer.name == "Мультиголова":
                        validate_disjoint(multihead_cleaning, process, distance=1, ordered=True)

        # add multihead to "extra_packings"
        for multihead_cleaning in self.m.root["extra"].iter(cls="multihead_cleaning"):
            push(self.m.root["extra_packings"], multihead_cleaning, push_func=add_push)

        # add packings to "extra_packings"
        for packing in self.m.root["extra"].iter(cls="packing"):
            push(
                self.m.root["extra_packings"],
                packing,
                push_func=AxisPusher(start_from=int(packing.props["extra_props"]["start_from"])),
                validator=ExtraValidator(),
            )

    def _process_cleanings(self):
        # - Add cleanings if necessary

        # extract boilings

        for line_name in [LineName.WATER, LineName.SALT]:
            boilings = self.m.root["master"]["boiling", True]
            boilings = [b for b in boilings if b.props["boiling_model"].line.name == line_name]
            boilings = list(sorted(boilings, key=lambda b: b.x[0]))

            for a, b in iter_pairs(boilings):
                rest = b["pouring"]["first"]["termizator"].x[0] - a["pouring"]["first"]["termizator"].y[0]

                # extract current cleanings
                cleanings = list(
                    self.m.root["master"].iter(
                        cls="cleaning",
                        line_name=line_name,
                    )
                )

                # calc in_between and previous cleanings
                in_between_cleanings = [c for c in cleanings if a.x[0] <= c.x[0] <= b.x[0]]
                previous_cleanings = [c for c in cleanings if c.x[0] <= a.x[0]]
                if previous_cleanings:
                    previous_cleaning = max(previous_cleanings, key=lambda c: c.x[0])
                else:
                    previous_cleaning = None

                if not in_between_cleanings:
                    # no current in between cleanings -> try to add if needed

                    # if rest is more than an hour and less than 80 minutes -> short cleaning
                    if rest >= 24:
                        cleaning = make_termizator_cleaning_block(
                            "short",
                            rule="rest_after_two_hours",
                            line_name=line_name,
                        )
                        cleaning.props.update(x=(a["pouring"]["first"]["termizator"].y[0] - self.m.root.x[0], 0))
                        push(self.m.root["master"], cleaning, push_func=add_push)

        # - Add last full cleaning

        for line_name in [LineName.WATER, LineName.SALT]:
            last_boiling = self.get_latest_boiling(line_name=line_name)
            if last_boiling:
                start_from = (
                    last_boiling["pouring"]["first"]["termizator"].y[0] + 1 - self.m.root.x[0]
                )  # add five extra minutes
                push(
                    self.m.root["master"],
                    make_termizator_cleaning_block(
                        "full",
                        rule="closing",
                        line_name=line_name,
                    ),
                    push_func=AxisPusher(start_from=start_from),
                    validator=Validator(),
                )

    def _process_shifts(self):
        # - Cheese makers

        beg = (
            min(self.m.root["master"]["boiling", True], key=lambda b: b.x[0]).x[0] - 6 - self.m.root.x[0]
        )  # 0.5h before start
        end = (
            max(self.m.root["master"]["boiling", True], key=lambda b: b.y[0])["pouring"]["second"]["pouring_off"].y[0]
            + 24
        ) - self.m.root.x[0]  # 2h after last pouring off
        shifts = split_shifts(beg, end)

        for i, (beg, end) in enumerate(shifts, 1):
            push(
                self.m.root["shifts"]["cheese_makers"],
                push_func=add_push,
                block=self.m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
            )

        # - Water

        # todo maybe: refactor, code duplication [@marklidenberg]
        water_boilings = [
            b for b in self.m.root["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.WATER
        ]

        if water_boilings:
            # - Water meltings

            beg = water_boilings[0]["melting_and_packing"]["melting"].x[0] - 12 - self.m.root.x[0]  # 1h before start
            end = water_boilings[-1]["melting_and_packing"]["melting"].y[0] + 12 - self.m.root.x[0]  # 1h after end

            shifts = split_shifts(beg, end)

            for i, (beg, end) in enumerate(shifts, 1):
                push(
                    self.m.root["shifts"]["water_meltings"],
                    push_func=add_push,
                    block=self.m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
                )

            # - Water packings

            beg = water_boilings[0]["melting_and_packing"]["packing"].x[0] - 18 - self.m.root.x[0]  # 1.5h before start
            end = water_boilings[-1]["melting_and_packing"]["packing"].y[0] + 6 - self.m.root.x[0]  # 0.5h after end

            shifts = split_shifts(beg, end)

            for i, (beg, end) in enumerate(shifts, 1):
                push(
                    self.m.root["shifts"]["water_packings"],
                    push_func=add_push,
                    block=self.m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
                )

        # - Salt

        salt_boilings = [
            b for b in self.m.root["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.SALT
        ]
        if salt_boilings:
            # - Salt meltings

            beg = salt_boilings[0]["melting_and_packing"]["melting"].x[0] - 12 - self.m.root.x[0]  # 1h before start
            end = (
                salt_boilings[-1]["melting_and_packing"]["packing", True][-1].y[0] - self.m.root.x[0]
            )  # end of packing

            shifts = split_shifts(beg, end)

            for i, (beg, end) in enumerate(shifts, 1):
                push(
                    self.m.root["shifts"]["salt_meltings"],
                    push_func=add_push,
                    block=self.m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
                )

            # - Salt packings

            try:
                beg = (
                    salt_boilings[0]["melting_and_packing"]["packing", True][0].x[0] - 12 - self.m.root.x[0]
                )  # 1h before start
                end = (
                    salt_boilings[-1]["melting_and_packing"]["packing", True][-1].y[0] + 6 - self.m.root.x[0]
                )  # 0.5h after end

                shifts = split_shifts(beg, end)

                for i, (beg, end) in enumerate(shifts, 1):
                    push(
                        self.m.root["shifts"]["salt_packings"],
                        push_func=add_push,
                        block=self.m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
                    )
            except:
                pass

    def make(
        self,
        boilings,
        date=None,
        cleanings=None,
        start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
        start_configuration=None,
    ):
        # - Arguments

        self.start_configuration = start_configuration or []
        self.date = date or datetime.now()
        self.cleanings = cleanings or {}  # {boiling_id: cleaning}
        self.boilings = boilings

        # - Start times

        # -- Set start_times

        self.start_times = {k: v if v else None for k, v in start_times.items()}

        # -- Add a flag that time has been set

        self.is_time_set = False

        # - Other

        self._init_block_maker()
        self._init_lines_df()
        self._init_left_df()
        self._init_multihead_water_boilings()
        self._process_boilings()
        self._process_extras()
        self._process_cleanings()
        self._process_shifts()
        return self.m.root


def make_schedule_basic(
    boiling_plan_obj,
    cleanings=None,
    start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
    start_configuration=None,
    date=None,
    first_batch_ids_by_type: dict = {"mozzarella": 1},
):
    logger.info(
        "Making basic_example schedule",
        start_times=start_times,
        start_configuration=start_configuration,
        cleanings=cleanings,
    )

    # - Make schedule

    return ScheduleMaker().make(
        boilings=make_boilings(
            to_boiling_plan(
                boiling_plan_obj,
                first_batch_ids_by_type=first_batch_ids_by_type,
            )
        ),
        date=date,
        cleanings=cleanings,
        start_times=dict(start_times),
        start_configuration=start_configuration,
    )
