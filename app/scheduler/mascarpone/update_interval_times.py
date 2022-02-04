from app.imports.runtime import *
from app.scheduler.mascarpone.parser_new import  parse_schedule


def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, 'Расписание'))
    boiling_plan_df['interval_time'] = None
    boiling_plan_df['start'] = ''
    boiling_plan_df['finish'] = ''

    with code('fill cream cheese and cottage cheese'):
        boilings = [b for b in schedule_info.get('cream_cheese_boilings', []) if b['type'] == 'cream_cheese']
        boilings = list(sorted(boilings, key=lambda b: b['interval'][0]))
        if len(boilings) > 0:
            grouped = list(boiling_plan_df[boiling_plan_df['type'] == 'cream_cheese'].groupby('group_id'))
            grouped = sorted(grouped, key=lambda v: v[1].index[0])
            for i, (_, grp) in enumerate(grouped):
                boiling_plan_df.loc[grp.index, 'start'] = boilings[i]['interval_time'][0]
                boiling_plan_df.loc[grp.index, 'finish'] = boilings[i]['interval_time'][1]

    with code('fill mascarpone and cream'):
        if len(schedule_info.get('mascarpone_boiling_groups', [])) > 0:
            for boiling_type in ['cream', 'mascarpone']:
                if len(boiling_plan_df['full_type'] == boiling_type) == 0:
                    continue
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