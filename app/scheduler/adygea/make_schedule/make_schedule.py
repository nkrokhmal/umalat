import itertools

import pandas as pd

from more_itertools import last, nth
from utils_ak.block_tree import Block
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.iteration.simple_iterator import iter_sequences
from utils_ak.portion.portion_tools import cast_interval

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import AdygeaLine, Washer, cast_model
from app.scheduler.adygea.make_schedule._boilings import make_boiling, make_cleaning, make_lunch, make_preparation
from app.scheduler.adygea.make_schedule.validator import Validator
from app.scheduler.adygea.to_boiling_plan.to_boiling_plan import to_boiling_plan
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.time_utils import cast_t, cast_time


""" 

There are 4 sublines: 0, 1, 2, 3. Also called boilers (in code, boiler_num) 

They are split into pairs: 0-1: pair_num=0, 2-3: pair_num=1
Each pair has it's own lunch (zero or one for each pair) 

Boilings are pushed in the following order of sublines: 0, 2, 1, 3

Halumi is made on sublines 2 and 3

"""


def _make_schedule(
    boiling_plan_df: pd.DataFrame,
    start_time: str = "07:00",
    lunch_times: list[str] = [],
) -> Block:
    """
    Parameters
    ----------
    boiling_plan_df: pd.DataFrame
        План варок
    start_time: str
        Когда начинается расписание
    lunch_times
        Время обедов
    Returns
    -------
    Block
        Расписание
    """

    # - Validate lunch times

    lunch_times = list(lunch_times)  # copy to avoid side effects
    assert len(lunch_times) in [0, 2]  # no lunches or two lunches for two teams

    # - Get some models

    adygea_line = cast_model(cls=AdygeaLine, obj="Адыгейский")
    adygea_cleaning = cast_model(Washer, "adygea_cleaning")

    # - Init block maker with preparation

    m = BlockMaker("schedule")
    m.push_row(
        make_preparation(adygea_line.preparation_time // 5),
        push_func=add_push,
        x=cast_t(start_time) - adygea_line.preparation_time // 5,
    )

    # - Copy boiling plan to avoid side effects

    boiling_plan_df = boiling_plan_df.copy()

    """
     batch_id            sku  n_baths    kg            boiling
0            1  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
1            2  <AdygeaSKU 1>        1  50.0  <AdygeaBoiling 1>
..."""

    boiling_num_generator = itertools.cycle(
        [0, 2, 1, 3]
    )  # there are 4 "sublines", one for each boiler. We insert boilings in that order

    for batch_id, grp in boiling_plan_df.groupby("batch_id"):

        # - Take first row as sample (any row is fine)

        sample_row = grp.iloc[0]

        # - Get next boiler number

        cur_boiler_num = next(boiling_num_generator)

        # - Get pair num

        pair_num = 0 if cur_boiler_num in [0, 1] else 1  # [2, 3] -> 1

        # - Make boiling

        boiling = make_boiling(
            sample_row["boiling"],
            batch_id=batch_id,
            boiler_num=cur_boiler_num,
            group_name=sample_row["sku"].group.name,
            pair_num=pair_num,
        )

        # - Push boiling

        push(
            m.root,
            boiling,
            push_func=AxisPusher(
                start_from="max_beg",
                start_shift=-30,
                min_start=cast_t(start_time),
            ),
            validator=Validator(),
        )

        # - Push lunch if needed

        if lunch_times:
            if lunch_times[pair_num] and cast_time(boiling.y[0]) >= lunch_times[pair_num]:
                push(
                    m.root,
                    make_lunch(size=adygea_line.lunch_time // 5, pair_num=pair_num),
                    push_func=AxisPusher(start_from=cast_t(lunch_times[pair_num])),
                    validator=Validator(),
                )
                lunch_times[pair_num] = None  # pushed lunch, delete lunch time

    # - Push lunches if finished earlier

    for pair_num, lunch_time in enumerate(lunch_times):
        # if processed before, deleted from corrected_lunch_times

        if lunch_time:
            push(
                m.root,
                make_lunch(size=adygea_line.lunch_time // 5, pair_num=pair_num),
                push_func=AxisPusher(start_from=cast_t(lunch_time)),
                validator=Validator(),
            )

    # - Add halumi boilings

    ...

    # - Push cleaning

    # -- Get last boilings

    last_boilings = [
        last(
            [boiling for boiling in m.root["boiling", True] if boiling.props["boiler_num"] == boiler_num],
            default=None,
        )
        for boiler_num in range(4)
    ]
    last_boilings = [b for b in last_boilings if b]

    # -- Get cleaning start

    cleaning_start = min(b.y[0] for b in last_boilings)
    if len(m.root["lunch", True]) > 0:
        cleaning_start = max(cleaning_start, min(b.y[0] for b in m.root["lunch", True]))

    # -- Push

    m.push_row(make_cleaning(size=adygea_cleaning.time // 5), x=cleaning_start, push_func=add_push)

    # - Start schedule from preparation

    # Because use used absolute final time in schedule creation, we need to update childrens x to be relative to the start time

    for child in m.root.children:
        child.props.update(x=(child.x[0] - cast_t(start_time) + adygea_line.preparation_time // 5, 0))

    m.root.props.update(x=(cast_t(start_time) - adygea_line.preparation_time // 5, 0))

    # - Return

    return m.root


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"adygea": 1},
) -> dict:

    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(boiling_plan, first_batch_ids_by_type=first_batch_ids_by_type)

    # - Find lunch times

    # We first build a schedule without lunch and find lunch times from it

    no_lunch_schedule = _make_schedule(boiling_plan_df, start_time=start_time)

    need_a_break = no_lunch_schedule.y[0] - no_lunch_schedule.x[0] >= 8 * 12  # work more than 8 hours
    if not need_a_break:
        # no lunch

        lunch_times = []
    else:
        lunch_times = []

        # - Go though each pair of boilers separately and find lunch time

        for i, rng in enumerate([range(0, 2), range(2, 4)]):
            # - Get boilings

            range_boilings = [
                boiling for boiling in no_lunch_schedule["boiling", True] if boiling.props["boiler_num"] in rng
            ]

            # - Calc helpers

            working_interval = cast_interval(no_lunch_schedule.x[0], no_lunch_schedule.y[0])
            lunch_interval = cast_interval(cast_t("12:00"), cast_t("14:30"))

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

    # - Make schedule with lunch times

    schedule = _make_schedule(
        boiling_plan_df,
        start_time=start_time,
        lunch_times=lunch_times,
    )

    # - Return

    return {"schedule": schedule, "boiling_plan_df": boiling_plan_df}


def test():
    print(
        make_schedule(
            str(get_repo_path() / "app/data/static/samples/by_department/adygea/sample_schedule_adygea.xlsx"),
        )["schedule"],
    )


if __name__ == "__main__":
    test()
