from utils_ak.interactive_imports import *
from app.schedule_maker.algo.schedule.schedule import *
from app.schedule_maker.algo.schedule.boilings import *
from app.schedule_maker.algo.stats import *
from pprint import pprint


def make_schedule_with_boiling_inside_a_day(boiling_plan_df):
    res = {}
    boilings = make_boilings_by_groups(boiling_plan_df)

    for i in tqdm(range(len(boilings) + 1)):
        boilings = make_boilings_by_groups(boiling_plan_df)
        cleaning_boiling = ([None] + boilings)[i]
        schedule = make_schedule(boilings, cleaning_boiling=cleaning_boiling, start_times={LineName.WATER: '08:00', LineName.SALT: '07:00'})
        res[i] = calc_schedule_stats(schedule)

    pprint(res)
    res = {k: v for k, v in res.items() if v['max_non_full_cleaning_time'] < '12:00'}
    best = min(res.items(), key=lambda v: v[1]['total_time'])
    print('Best', best[0], best[1])

    boilings = make_boilings_by_groups(boiling_plan_df)
    return make_schedule(boilings, cleaning_boiling=([None] + boilings)[best[0]], start_times={LineName.WATER: '08:00', LineName.SALT: '07:00'})