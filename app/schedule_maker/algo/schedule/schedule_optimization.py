from utils_ak.interactive_imports import *
from app.schedule_maker.algo.schedule.schedule import *
from app.schedule_maker.algo.schedule.boilings import *
from app.schedule_maker.algo.stats import *


def make_schedule_with_boiling_inside_a_day(boiling_plan_df, start_times=None):
    start_times = start_times or {LineName.WATER: '08:00', LineName.SALT: '07:00'}
    res = {}
    boilings = make_boilings(boiling_plan_df)

    cleaning_boilings = [None] + boilings[0:len(boilings) - 1]

    for cleaning_boiling in tqdm(cleaning_boilings):
        boilings = make_boilings(boiling_plan_df)
        schedule = make_schedule(boilings, cleaning_boiling=cleaning_boiling, start_times=start_times)
        res[cleaning_boiling] = calc_schedule_stats(schedule)

        if not cleaning_boiling and res[cleaning_boiling]['max_non_full_cleaning_time'] < '12:00':
            # no further search needed
            break

    res = {k: v for k, v in res.items() if v['max_non_full_cleaning_time'] < '12:00'}
    best = min(res.items(), key=lambda v: v[1]['total_time'])
    boilings = make_boilings(boiling_plan_df)
    return make_schedule(boilings, cleaning_boiling=best[0], start_times=start_times)
