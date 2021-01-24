from utils_ak.interactive_imports import *
from app.schedule_maker.algo.schedule.schedule import *
from app.schedule_maker.algo.schedule.boilings import *
from app.schedule_maker.algo.stats import *

# todo: refactor
def make_schedule_with_boiling_inside_a_day(boiling_plan_df, start_times=None):
    start_times = start_times or {LineName.WATER: '08:00', LineName.SALT: '07:00'}
    res = {}

    boilings = make_boilings(boiling_plan_df)

    for i in tqdm(range(len(boilings))):
        boilings = make_boilings(boiling_plan_df)
        cleaning_boilings = [None] + boilings[0:len(boilings) - 1]
        cleaning_boiling = cleaning_boilings[i]
        schedule = make_schedule(boilings, cleaning_boiling=cleaning_boiling, start_times=start_times)
        res[i] = calc_schedule_stats(schedule)

        if not cleaning_boiling and cast_t(res[i]['max_non_full_cleaning_time']) < cast_t('12:00'):
            # no further search needed
            break

        # todo: del, for faster result only - find first one only
        if cast_t(res[i]['max_non_full_cleaning_time']) < cast_t('12:00'):
            break

    suitable = {k: v for k, v in res.items() if cast_t(v['max_non_full_cleaning_time']) < cast_t('12:00')}

    # todo: uncom
    # assert len(suitable) > 0, 'Не получилось вставить мойку термизатора с учетом правила отсутствия непрерывной работы термизатора на протяжении 12 часов подряд. '
    # todo: delete
    if suitable:
        res = suitable

    best = min(res.items(), key=lambda v: v[1]['total_time'])
    boilings = make_boilings(boiling_plan_df)
    cleaning_boilings = [None] + boilings[0:len(boilings) - 1]
    cleaning_boiling = cleaning_boilings[best[0]]
    return make_schedule(boilings, cleaning_boiling=cleaning_boiling, start_times=start_times)
