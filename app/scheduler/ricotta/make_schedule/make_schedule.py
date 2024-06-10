import pandas as pd

from more_itertools import first, last
from utils_ak.block_tree import add_push
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.validation.class_validator import ClassValidator
from utils_ak.block_tree.validation.validate_disjoint import validate_disjoint

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.split_shifts_utils import split_shifts_by_time
from app.scheduler.common.time_utils import cast_t
from app.scheduler.ricotta.make_schedule._make_boilings import _make_boilings
from app.scheduler.ricotta.to_boiling_plan import to_boiling_plan


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=100)

    @staticmethod
    def validate__boiling__boiling(b1, b2):

        # - Validate main

        validate_disjoint(b1["pouring"], b2["pouring"], ordered=True)
        validate_disjoint(b1["pumping"], b2["pumping"], ordered=True)
        validate_disjoint(b1["packing"], b2["packing"], ordered=True)

        if b1.props["floculator_num"] == b2.props["floculator_num"]:
            validate_disjoint(b1["draw_whey"], b2["heating"])
        if b1.props["drenator_num"] == b2.props["drenator_num"]:
            validate_disjoint(
                b1["pumping"],
                b2["dray_ricotta"],
                ordered=True,
                distance=8 if b2.props["is_manual_cleaning_needed"] else 0,
            )

        # - Validate pumping # todo next: mark, ask guys [@marklidenberg]

        # -- Calculate current lag between pumping and packing

        current_lag = b1["packing"].y[0] - b1["pumping"].y[0]
        assert current_lag >= 0, "Packing should be after pumping"
        new_lag = current_lag + b2["packing"].size[0] - b1["pumping"].size[0]
        new_lag = max(1, new_lag)  # lag cannot be less than 1

        # -- Calculate buffer tank distance to meet capacity requirements

        # min_pumping_start_to_not_overfill_buffer_tank = 0
        # left_kg = 1000 * 0.5  # buffer tank size with 20% reserve
        # for is_first, is_last, packing in mark_ends(b2["packing", True] + list(reversed(b1["packing", True]))):
        #     if packing.props["kg"] <= left_kg:
        #         left_kg -= packing.props["kg"]
        #         continue
        #     else:
        #         # finish here
        #         min_pumping_start_to_not_overfill_buffer_tank = (
        #             packing.y[0] if not is_first else b1["packing"].y[0] + b2["packing"].size[0]
        #         ) - left_kg / packing.props["kg"] * packing.size[0]
        #         min_pumping_start_to_not_overfill_buffer_tank = math.ceil(min_pumping_start_to_not_overfill_buffer_tank)
        #         break
        #
        # min_distance_to_not_overfill_buffer_tank = max(
        #     0, (min_pumping_start_to_not_overfill_buffer_tank - b2["pumping"].size[0] - b1["pumping"].y[0])
        # )
        #
        # # -- Validate
        #
        # validate_disjoint_by_axis(
        #     b1["pumping"],
        #     b2["pumping"],
        #     distance=max(min(3, new_lag - 1), min_distance_to_not_overfill_buffer_tank),
        #     ordered=True,
        # )

        # - Validate packing and pumping

        if b1.props["percent"] != b2.props["percent"]:  # todo next: mark, ask guys [@marklidenberg]
            validate_disjoint(b1["packing"], b2["pumping"], ordered=True)

        # - Validate extra processinng

        validate_disjoint(b1["extra_processing"], b2["dray_ricotta"], ordered=True)

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        if b2.props["cleaning_object"] == "floculator" and b1.props["floculator_num"] == b2.props["floculator_num"]:
            validate_disjoint(b1["dray_ricotta"], b2, ordered=True)

    @staticmethod
    def validate__cleaning__cleaning(b1, b2):
        validate_disjoint(b1, b2, ordered=True, distance=1)


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_time="07:00",
    first_batch_ids_by_type: dict = {"ricotta": 1},
) -> dict:

    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(boiling_plan, first_batch_ids_by_type=first_batch_ids_by_type).copy()

    # - Init block maker

    m = BlockMaker("schedule")

    # - Make preparation block

    m.push_row(
        "preparation",
        size=6,
        push_func=AxisPusher(start_from=cast_t(start_time)),
        push_kwargs={"validator": Validator()},
    )

    # - Make boilings

    current_floculator_num = 0
    current_drenator_num = 0
    for i, (idx, grp) in enumerate(boiling_plan_df.groupby("batch_id")):

        # - Prepare boiling

        boilings = _make_boilings(grp, first_floculator_num=current_floculator_num)

        # - Insert new boiling

        for j, boiling in enumerate(boilings):

            # - Check if manual cleaning is needed

            # -- Get drenator objects

            drenator_boilings = [
                b for b in m.root["boiling", True] if b.props["drenator_num"] == (current_drenator_num + j) % 2 + 1
            ]
            drenator_cleanings = [
                c
                for c in m.root["manual_cleaning", True]
                if c.props["drenator_num"] == (current_drenator_num + j) % 2 + 1
            ]

            # -- Get if manual cleaning is needed

            is_manual_cleaning_needed = False
            if drenator_cleanings:
                drenator_boilings = [
                    b for b in drenator_boilings if b["dray_ricotta"].x[0] > drenator_cleanings[-1].x[0]
                ]

            if drenator_boilings:
                is_manual_cleaning_needed = (
                    drenator_boilings[-1]["dray_ricotta"].x[0] - drenator_boilings[0]["dray_ricotta"].y[0]
                ) > cast_t("06:00")

            # - Push block

            m.push(
                boiling,
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
                floculator_num=(current_floculator_num + j) % 3 + 1,
                drenator_num=(current_drenator_num + j) % 2 + 1,
                is_manual_cleaning_needed=is_manual_cleaning_needed,
            )

            # - Push manual cleaning if needed

            if is_manual_cleaning_needed:
                m.push(
                    "manual_cleaning",
                    size=(8, 0),
                    x=(boiling["dray_ricotta"].x[0] - 8, 0),
                    push_func=add_push,
                    drenator_num=(current_drenator_num + j) % 2 + 1,
                )

        current_floculator_num += len(boilings)
        current_drenator_num += len(boilings)

    # - Add cleanings

    for floculator_num in [floculator.props["floculator_num"] for floculator in m.root.iter(cls="boiling")][-3:]:
        m.push(
            "cleaning",
            size=(12, 0),
            push_func=AxisPusher(start_from="last_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
            cleaning_object="floculator",
            floculator_num=floculator_num,
        )

    for cleaning_object in ["drenator", "lishat_richi", "buffer_tank"]:
        m.push_row(
            "cleaning",
            size=20 if cleaning_object == "drenator" else 12,
            push_func=AxisPusher(start_from="last_beg", start_shift=-50),
            push_kwargs={"validator": Validator()},
            cleaning_object=cleaning_object,
        )

    # - Make shifts

    # -- Brigadir

    for i, (a, b) in enumerate(
        split_shifts_by_time(
            a=next(m.root.iter(cls="preparation")).y[0],
            b=last(m.root.iter(cls="cleaning", cleaning_object="lishat_richi")).y[0],
            split=cast_t("18:00"),
            min_shift=6,
        )
    ):
        m.push("shift", size=(b - a, 0), x=(a, 0), push_func=add_push, team="Бригадир", shift_num=i)

    # -- Packing

    for i, (a, b) in enumerate(
        split_shifts_by_time(
            a=first(m.root.iter(cls="packing")).x[0] - 12,
            b=last(m.root.iter(cls="packing")).y[0] + 12,
            split=cast_t("18:00"),
            min_shift=6,
        )
    ):
        m.push("shift", size=(b - a, 0), x=(a, 0), push_func=add_push, team="Упаковка", shift_num=i)

    # - Return result

    return {"schedule": m.root, "boiling_plan_df": boiling_plan_df}


def test():

    # - Configure pandas

    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)

    # - Make schedule

    schedule = make_schedule(
        str(get_repo_path() / "app/data/static/samples/by_department/ricotta/2024-05-06 Расписание рикотта.xlsx"),
    )["schedule"]

    print(schedule)


if __name__ == "__main__":
    test()
