from app.scheduler.mozzarella.boiling_plan import read_boiling_plan
from app.scheduler.mozzarella.algo.schedule.find_optimal_cleanings.find_optimal_cleanings_combination_by_schedule import (
    find_optimal_cleanings_combination_by_schedule,
)
from app.scheduler.mozzarella.algo.schedule.make_schedule_from_boilings.make_schedule_from_boilings import *
from app.scheduler.mozzarella.algo.schedule.make_boilings import make_boilings
from app.scheduler.mozzarella.algo.stats import *


def find_optimal_cleanings(
    boiling_plan_df: pd.DataFrame,
    start_times: Optional[dict] = None,
    **make_schedule_kwargs,
):

    # - Preprocess arguments

    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}

    # - Make boilings

    boilings = make_boilings(boiling_plan_df)

    # - Make schedule

    schedule = make_schedule_from_boilings(boilings, start_times=start_times, **make_schedule_kwargs)

    # - Find optimal cleanings combination

    return find_optimal_cleanings_combination_by_schedule(schedule)


def test():
    # - Configure loguru

    utils.configure_loguru(level="DEBUG")

    # - Load boiling_plan_df

    boiling_plan_fn = r"/Users/arsenijkadaner/FileApps/coding_projects/umalat/app/data/static/samples/inputs/by_department/mozzarella/План по варкам моцарелла 2023-06-02.xlsx"
    boiling_plan_df = read_boiling_plan(boiling_plan_fn)

    # - Find optimal cleanings

    print(
        find_optimal_cleanings(
            boiling_plan_df=boiling_plan_df,
            start_times={LineName.WATER: "08:00", LineName.SALT: "07:00"},
        )
    )

if __name__ == '__main__':
    test()