import itertools

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis
from utils_ak.builtin.collection import iter_get
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.iteration.simple_iterator import iter_sequences
from utils_ak.portion.portion_tools import cast_interval

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import AdygeaLine, Washer, cast_model
from app.scheduler.adygea.make_schedule._boilings import make_boiling, make_cleaning, make_lunch, make_preparation
from app.scheduler.adygea.to_boiling_plan.to_boiling_plan import to_boiling_plan
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.time_utils import cast_t, cast_time


BOILING_NUMS = [0, 2, 1, 3]


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=30)

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1["collecting"], b2["collecting"])
        if b1.props["boiler_num"] == b2.props["boiler_num"]:
            if b1.props["boiling_model"].weight_netto != b2.props["boiling_model"].weight_netto:
                validate_disjoint_by_axis(b1, b2, ordered=True, distance=2)
            else:
                validate_disjoint_by_axis(b1, b2)

        if b2.parent["boiling", True].index(b2) <= 3 and b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint_by_axis(b1["coagulation"], b2["coagulation"], ordered=True)

    @staticmethod
    def validate__boiling__lunch(b1, b2):
        if b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__boiling(b1, b2):
        if b1.props["pair_num"] == b2.props["pair_num"]:
            validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__lunch(b1, b2):
        pass


def _make_schedule(
    boiling_plan_df,
    start_time="07:00",
    prepare_start_time="07:00",
    lunch_times=None,
):
    lunch_times = lunch_times or []
    lunch_times = list(lunch_times)
    assert len(lunch_times) in [0, 2]  # no lunches or two lunches for two teams

    adygea_line = cast_model(cls=AdygeaLine, obj="Адыгейский")

    local_start_t = cast_t(start_time) - cast_t(prepare_start_time)
    normed_lunch_times = [cast_time(cast_t(lt) - cast_t(prepare_start_time)) for lt in lunch_times]

    m = BlockMaker("schedule")
    m.row(make_preparation(adygea_line.preparation_time // 5), push_func=add_push)

    boiling_plan_df = boiling_plan_df.copy()

    """example: boiling_plan_df example
     batch_id            sku  n_baths    kg            boiling
0            1  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
1            2  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
2            3  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
3            4  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
4            5  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
5            6  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
6            7  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
7            8  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
8            9  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
9           10  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
10          11  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
11          12  <AdygeaSKU 1>        1   8.0  <AdygeaBoiling 1>
12          12  <AdygeaSKU 2>        1   9.0  <AdygeaBoiling 1>
13          12  <AdygeaSKU 3>        1  33.0  <AdygeaBoiling 1>
14          13  <AdygeaSKU 3>        1  50.0  <AdygeaBoiling 1>
15          14  <AdygeaSKU 3>        1  44.0  <AdygeaBoiling 1>
16          14  <AdygeaSKU 4>        1   6.0  <AdygeaBoiling 1>
17          15  <AdygeaSKU 5>        1  50.0  <AdygeaBoiling 2>
18          16  <AdygeaSKU 5>        1  50.0  <AdygeaBoiling 2>
19          17  <AdygeaSKU 5>        1  50.0  <AdygeaBoiling 2>
20          18  <AdygeaSKU 5>        1  50.0  <AdygeaBoiling 2>"""

    adygea_cleaning = cast_model(Washer, "adygea_cleaning")

    boiling_num_generator = itertools.cycle(BOILING_NUMS)

    # todo maybe: a little bit messy with batch_id, cur_batch_id and n_baths [@marklidenberg]
    for batch_id, grp in boiling_plan_df.groupby("batch_id"):
        row = grp.iloc[0]
        cur_boiler_num = next(boiling_num_generator)
        pair_num = BOILING_NUMS.index(cur_boiler_num) % 2
        boiling = make_boiling(
            row["boiling"],
            batch_id=batch_id,
            boiler_num=cur_boiler_num,
            group_name=row["sku"].group.name,
            pair_num=pair_num,
        )
        push(
            m.root,
            boiling,
            push_func=AxisPusher(start_from="max_beg", start_shift=-30, min_start=local_start_t),
            validator=Validator(),
        )
        with code("Push lunch if needed"):
            if normed_lunch_times:
                if normed_lunch_times[pair_num] and cast_time(boiling.y[0]) >= normed_lunch_times[pair_num]:
                    push(
                        m.root,
                        make_lunch(size=adygea_line.lunch_time // 5, pair_num=pair_num),
                        push_func=AxisPusher(start_from=cast_t(normed_lunch_times[pair_num]), min_start=local_start_t),
                        validator=Validator(),
                    )
                    normed_lunch_times[pair_num] = None  # pushed lunch, nonify lunch time

    with code("Push lunches if not pushed yet"):
        for pair_num, lunch_time in enumerate(normed_lunch_times):
            if lunch_time:
                push(
                    m.root,
                    make_lunch(size=adygea_line.lunch_time // 5, pair_num=pair_num),
                    push_func=AxisPusher(start_from=cast_t(lunch_time), min_start=local_start_t),
                    validator=Validator(),
                )

    with code("Cleaning"):
        last_boilings = [
            iter_get([boiling for boiling in m.root["boiling", True] if boiling.props["boiler_num"] == boiler_num], -1)
            for boiler_num in range(4)
        ]
        last_boilings = [b for b in last_boilings if b]
        cleaning_start = min(b.y[0] for b in last_boilings)
        if len(m.root["lunch", True]) > 0:
            cleaning_start = max(cleaning_start, min(b.y[0] for b in m.root["lunch", True]))
        m.row(make_cleaning(size=adygea_cleaning.time // 5), x=cleaning_start, push_func=add_push)

    m.root.props.update(x=(cast_t(prepare_start_time), 0))
    return m.root


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    prepare_start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"adygea": 1},
) -> dict:
    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(boiling_plan, first_batch_ids_by_type=first_batch_ids_by_type)

    # - Make scedule

    no_lunch_schedule = _make_schedule(boiling_plan_df, start_time=start_time, prepare_start_time=prepare_start_time)

    need_a_break = no_lunch_schedule.y[0] - no_lunch_schedule.x[0] >= 8 * 12  # work more than 8 hours
    if not need_a_break:
        # no lunch in these cases
        lunch_times = []

        # print('No lunch needed')
    else:
        lunch_times = []
        for i, r in enumerate([range(0, 2), range(2, 4)]):
            range_boilings = [
                boiling for boiling in no_lunch_schedule["boiling", True] if boiling.props["boiler_num"] in r
            ]

            def find_first_after(time):
                for b1, b2, b3 in iter_sequences(range_boilings, 3, method="any"):
                    if not b2:
                        continue
                    if b2.y[0] >= cast_t(time):
                        if b3 and b1:
                            if b2.y[0] - b1.y[0] >= b3.y[0] - b2.y[0]:
                                # wait for next boiling and make lunch
                                return cast_time(b3.y[0])
                            else:
                                # make lunch now
                                return cast_time(b2.y[0])
                        else:
                            # make lunch now
                            return cast_time(b2.y[0])

                raise Exception("Did not find lunch time")

            working_interval = cast_interval(no_lunch_schedule.x[0], no_lunch_schedule.y[0])
            lunch_interval = cast_interval(cast_t("12:00"), cast_t("14:30"))

            if lunch_interval.upper - working_interval.lower <= working_interval.upper - lunch_interval.lower:
                # lunch is closer to the start
                if lunch_interval.upper - working_interval.lower >= 2 * 12:
                    lunch_times.append(find_first_after("00:13:30"))

                    # print(1, lunch_times)
                    continue

            else:
                # lunch is close to the end
                if working_interval.upper - lunch_interval.lower >= 2 * 12:
                    lunch_times.append(find_first_after("00:12:00"))

                    # print(2, lunch_times)
                    continue
                elif working_interval.upper - lunch_interval.lower >= 0:
                    # less than two hours till end - still possibly need a break
                    if need_a_break:
                        if lunch_interval.lower - working_interval.lower <= 7 * 12:
                            # work around 7 hours
                            lunch_times.append(find_first_after("00:12:00"))

                            # print(3, lunch_times)
                            continue

            if need_a_break:
                lunch_times.append(find_first_after(cast_time(no_lunch_schedule.x[0] + 6 * 12)))

                # print(4, lunch_times)
                continue
    schedule = _make_schedule(
        boiling_plan_df, start_time=start_time, prepare_start_time=prepare_start_time, lunch_times=lunch_times
    )

    return {"schedule": schedule, "boiling_plan_df": boiling_plan_df}


def test():
    print(
        make_schedule(
            str(
                get_repo_path()
                / "app/data/static/samples/by_department/adygea/2023-09-03 План по варкам милкпроджект.xlsx"
            )
        )
    )


if __name__ == "__main__":
    test()
