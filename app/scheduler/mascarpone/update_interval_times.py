from app.imports.runtime import *
from app.scheduler.mascarpone.parser_new import  parse_schedule


def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, 'Расписание'))
    boiling_plan_df['interval_time'] = None

    with code('fill cream cheese and cottage cheese'):
        boilings = [b for b in schedule_info['cream_cheese_boilings'] if b['type'] == 'cream_cheese']
        boilings = list(sorted(boilings, key=lambda b: b['interval'][0]))

        for i, ((full_type, batch_id), grp) in enumerate(
                boiling_plan_df[boiling_plan_df['type'] == 'cream_cheese'].groupby(['full_type', 'absolute_batch_id'])):
            boiling_plan_df.loc[grp.index, 'start'] = boilings[i]['interval_time'][0]
            boiling_plan_df.loc[grp.index, 'finish'] = boilings[i]['interval_time'][1]

    with code('fill mascarpone and cream'):
        for boiling_type in ['cream', 'mascarpone']:
            interval_times = {}

            for boiling in [b for b in schedule_info['mascarpone_boiling_groups'] if b['type'] == boiling_type]:
                interval_times[boiling['boiling_id']] = boiling['interval_time']

            boiling_plan_df['start'] = np.where(boiling_plan_df['full_type'] == boiling_type,
                                                boiling_plan_df['absolute_batch_id'].apply(
                                                    lambda batch_id: interval_times.get(batch_id, [None, None])[0]),
                                                boiling_plan_df['start'])
            boiling_plan_df['finish'] = np.where(boiling_plan_df['full_type'] == boiling_type,
                                                 boiling_plan_df['absolute_batch_id'].apply(
                                                     lambda batch_id: interval_times.get(batch_id, [None, None])[1]),
                                                 boiling_plan_df['finish'])
    return boiling_plan_df