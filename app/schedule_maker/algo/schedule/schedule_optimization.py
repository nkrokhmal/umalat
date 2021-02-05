from utils_ak.interactive_imports import *
from app.schedule_maker.algo.schedule.schedule import *
from app.schedule_maker.algo.schedule.boilings import *
from app.schedule_maker.algo.stats import *

# todo: refactor
def make_schedule_with_boiling_inside_a_day(boiling_plan_df, start_times=None, first_group_id=None):
    start_times = start_times or {LineName.WATER: '08:00', LineName.SALT: '07:00'}
    res = {}

    boilings = make_boilings(boiling_plan_df)
    # cleaning_boilings = [None] + boilings[0: len(boilings) - 1]

    for i in tqdm(range(len(boilings))):
        # small optimization. # todo: del
        # a = cleaning_boilings[1]['pouring']['first']['termizator'].y[0]
        # b = cleaning_boilings[i]['pouring']['first']['termizator'].y[0]
        # c = cleaning_boilings[-1]['pouring']['first']['termizator'].x[0]
        #
        # if cleaning_boilings[i] and c - b > cast_t('14:00') or b - a > cast_t('14:00')
        #     logger.info(f'Skipping boiling {i}')
        #     continue

        boilings = make_boilings(boiling_plan_df)
        cleaning_boilings = [None] + boilings[0:len(boilings) - 1]
        cleaning_boiling = cleaning_boilings[i]
        schedule = make_schedule(boilings, cleaning_boiling=cleaning_boiling, start_times=start_times)
        res[i] = calc_schedule_stats(schedule)

        if not cleaning_boiling and cast_t(res[i]['max_non_full_cleaning_time']) < cast_t('12:00'):
            # no further search needed
            break

        # # todo: del, for faster result only - find first one only
        # if cast_t(res[i]['max_non_full_cleaning_time']) < cast_t('12:00'):
        #     break

    suitable = {k: v for k, v in res.items() if cast_t(v['max_non_full_cleaning_time']) < cast_t('12:00')}

    # todo: uncom
    # assert len(suitable) > 0, 'Не получилось вставить мойку термизатора с учетом правила отсутствия непрерывной работы термизатора на протяжении 12 часов подряд. '
    # todo: delete
    if suitable:
        res = suitable
        best = min(res.items(), key=lambda v: v[1]['total_time'])
    else:
        # did not find any suitable - remove no cleaning suitable
        res.pop(0)
        # res_items = list(sorted(res.items(), key=lambda v: v[1]['max_non_full_cleaning_time']))[:12]
        best = min(res.items(), key=lambda v: v[1]['max_non_full_cleaning_time'])
    logger.info(f'Best cleaning_boiling: {best}')

    boilings = make_boilings(boiling_plan_df, first_group_id=first_group_id)
    cleaning_boilings = [None] + boilings[0:len(boilings) - 1]
    cleaning_boiling = cleaning_boilings[best[0]]
    return make_schedule(boilings, cleaning_boiling=cleaning_boiling, start_times=start_times)
