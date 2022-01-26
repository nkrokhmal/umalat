from app.scheduler.butter.parser_new import  parse_schedule


def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, 'Расписание'))

    # find boilings
    boilings = schedule_info['boilings']
    boilings = list(sorted(boilings, key=lambda b: b['interval'][0]))

    # set interval times
    interval_times = {}
    beg, end = boiling_plan_df['absolute_batch_id'].min(), boiling_plan_df['absolute_batch_id'].max() + 1
    for i, batch_id in enumerate(range(beg, end)):
        interval_times[batch_id] = boilings[i]['interval_time']
    boiling_plan_df['start'] = boiling_plan_df['absolute_batch_id'].apply(lambda batch_id: interval_times.get(batch_id)[0])
    boiling_plan_df['finish'] = boiling_plan_df['absolute_batch_id'].apply(lambda batch_id: interval_times.get(batch_id)[1])
    return boiling_plan_df