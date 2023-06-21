from app.imports.runtime import *

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.scheduler.shifts import *
from app.enum import LineName

from app.scheduler.mozzarella.algo.schedule.custom_pushers import *
from utils_ak.block_tree import *
from typing import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


class Validator(ClassValidator):
    def __init__(
        self,
        window: int = 20,
        strict_order: bool = False,
        sheet_order: bool = True,
        block_validator: Callable = validate_disjoint_by_axis,
        order_validator: Optional[Callable] = validate_order_by_axis,
    ):
        super().__init__(window=window)
        self.strict_order = strict_order
        self.sheet_order = sheet_order
        self.block_validator = block_validator
        self.order_validator = order_validator

    def validate__boiling__boiling(self, b1, b2):

        # - Sort

        b1s, b2s = min([b1, b2], key=lambda b: b.x[0]), max([b1, b2], key=lambda b: b.x[0])

        # - Unpack boiling models

        boiling_model1 = b1s.props["boiling_model"]
        boiling_model2 = b2s.props["boiling_model"]

        # - Basic validations

        self.block_validator(b1s["pouring"]["first"]["termizator"], b2s["pouring"]["first"]["termizator"])
        self.block_validator(b1s["pouring"]["second"]["pouring_off"], b2s["pouring"]["second"]["pouring_off"])
        self.block_validator(b1s["pouring"]["first"]["pumping_out"], b2s["pouring"]["second"]["pouring_off"])
        self.block_validator(b1s["pouring"]["second"]["pouring_off"], b2s["pouring"]["first"]["pumping_out"])

        # - Process boilings on the same pouring line

        if b1s["pouring"].props["pouring_line"] == b2s["pouring"].props["pouring_line"]:

            # pourings should not intersect, but also five minutes should be between boilings
            self.block_validator(b1s["pouring"], b2s["pouring"], distance=1, ordered=True)

            # if boilings use same drenator - drenator should not intersect with meltings
            if b1s.props["drenator_num"] == b2s.props["drenator_num"]:
                self.block_validator(b1s["melting_and_packing"]["melting"]["meltings"], b2s["drenator"])

        # - Define line names (water/salt) that we work on (which corresponds to the pouring line)

        wln1 = LineName.WATER if b1s["pouring"].props["pouring_line"] in ["0", "1"] else LineName.SALT
        wln2 = LineName.WATER if b2s["pouring"].props["pouring_line"] in ["0", "1"] else LineName.SALT

        # - Process boilings on the same line or on the same working line

        if boiling_model1.line.name == boiling_model2.line.name:
            # same lines

            # - Basic validation

            self.block_validator(
                b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["meltings"]
            )
            for p1, p2 in itertools.product(
                b1s["melting_and_packing"]["collecting", True], b2s["melting_and_packing"]["collecting", True]
            ):
                self.block_validator(p1, p2)

            # - If water and different boilings - cannot intersect serving with meltings

            if boiling_model1.line.name == LineName.WATER and boiling_model1 != boiling_model2:
                if not boiling_model1.is_lactose:
                    _df = b1s.props["boiling_group_df"]
                    _df["is_lactose"] = _df["sku"].apply(lambda sku: sku.made_from_boilings[0].is_lactose)
                    if not _df["is_lactose"].any():
                        if boiling_model1.percent == boiling_model2.percent:

                            # 3.3 бл неполная -> 3.3
                            self.block_validator(
                                b1s["melting_and_packing"]["melting"]["meltings"],
                                b2s["melting_and_packing"]["melting"]["serving"],
                                distance=-4,
                            )
                        else:

                            # 3.3 бл неполная -> 3.6
                            self.block_validator(
                                b1s["melting_and_packing"]["melting"]["meltings"],
                                b2s["melting_and_packing"]["melting"]["serving"],
                                distance=-2,
                            )
                    else:

                        # 3.3 бл полная -> 3.3/3.6
                        self.block_validator(
                            b1s["melting_and_packing"]["melting"]["meltings"],
                            b2s["melting_and_packing"]["melting"]["serving"],
                            distance=-2,
                        )
                elif boiling_model1.percent != boiling_model2.percent:

                    # 3.6, 3.3 - add extra 10 minutes
                    self.block_validator(
                        b1s["melting_and_packing"]["melting"]["meltings"],
                        b2s["melting_and_packing"]["melting"]["serving"],
                        distance=-2,
                    )
                else:

                    # 3.3 Альче Белзактозная -> 3.3 Сакко
                    self.block_validator(
                        b1s["melting_and_packing"]["melting"]["meltings"],
                        b2s["melting_and_packing"]["melting"]["serving"],
                    )

            # - There should be one hour pause between non-"Палочки 15/7" and "Палочки 15/7" form-factors

            mp1 = b1s["melting_and_packing"]["melting"]["meltings"]["melting_process", True][-1]
            mp2 = b2s["melting_and_packing"]["melting"]["meltings"]["melting_process", True][0]

            bff1_name = mp1.props["bff"].name
            bff2_name = mp2.props["bff"].name

            sticks = STICK_FORM_FACTOR_NAMES
            if bff1_name not in sticks and bff2_name in sticks:
                _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
                _b2s = b2s["melting_and_packing"]["melting"]["meltings"]

                # at least one hour should pass between meltings
                self.block_validator(_b1s, _b2s, distance=12, ordered=True)

            # - There should be one two hour pause between "Палочки 15/7" and non-"Палочки 15/7" form-factors

            mp1 = b1s["melting_and_packing"]["melting"]["meltings"]["melting_process", True][-1]
            mp2 = b2s["melting_and_packing"]["melting"]["meltings"]["melting_process", True][0]

            bff1_name = mp1.props["bff"].name
            bff2_name = mp2.props["bff"].name
            sticks = STICK_FORM_FACTOR_NAMES
            if bff1_name in sticks and bff2_name not in sticks:
                _b1s = b1s["melting_and_packing"]["melting"]["coolings"]
                _b2s = b2s["melting_and_packing"]["melting"]["coolings"]

                # at least one hour should pass between meltings
                self.block_validator(_b1s, _b2s, distance=24, ordered=True)

            # - Process lactose switch on salt line'

            if boiling_model1.line.name == LineName.SALT:
                if boiling_model1.is_lactose and not boiling_model2.is_lactose:
                    _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
                    _b2s = b2s["melting_and_packing"]["melting"]["serving"]
                    self.block_validator(_b1s, _b2s, distance=2, ordered=True)

                if not boiling_model1.is_lactose and boiling_model2.is_lactose:
                    _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
                    _b2s = b2s["melting_and_packing"]["melting"]["serving"]
                    self.block_validator(_b1s, _b2s, distance=-2, ordered=True)
        elif wln1 == wln2:
            # different lines

            # same working lines (means that salt and water on the same working line - due to salt switching to the first pouring_line)

            # - Basic validations

            self.block_validator(
                b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["meltings"]
            )
            self.block_validator(
                b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"]
            )

            # - There should be one hour pause between meltings on different lines

            _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
            _b2s = b2s["melting_and_packing"]["melting"]["meltings"]
            self.block_validator(_b1s, _b2s, distance=7, ordered=True)

        if self.order_validator:

            # - Process boilings in case of strict order

            if self.strict_order:
                self.order_validator(b1, b2)

            # - Order should be strict inside one configuration sheet

            if self.sheet_order and b1.props["sheet"] == b2.props["sheet"]:
                validate_order_by_axis(b1, b2)

    def validate__boiling__cleaning(self, b1, b2):
        boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        self.block_validator(boiling["pouring"]["first"]["termizator"], cleaning)

    def validate__cleaning__boiling(self, b1, b2):
        boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        self.block_validator(cleaning, boiling["pouring"]["first"]["termizator"])

    def validate__boiling__packing_configuration(self, b1, b2):
        boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        if boiling.props["boiling_model"].line.name != packing_configuration.props["line_name"]:
            return

        for p1 in boiling.iter(cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]):
            self.block_validator(p1, b2)

    def validate__packing_configuration__boiling(self, b1, b2):
        boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        if boiling.props["boiling_model"].line.name != packing_configuration.props["line_name"]:
            return

        for p1 in boiling.iter(cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]):
            self.block_validator(b1, p1)
