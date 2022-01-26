from app.scheduler.milk_project.parser_new import parse_schedule


def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, 'Расписание'))

    interval_times = {}

    for boiling in schedule_info['adygea_boilings']:
        interval_times[boiling['boiling_id']] = boiling['interval_time']

    boiling_plan_df['start'] = boiling_plan_df['batch_id'].apply(lambda batch_id: interval_times.get(batch_id)[0])
    boiling_plan_df['finish'] = boiling_plan_df['batch_id'].apply(lambda batch_id: interval_times.get(batch_id)[1])
    return boiling_plan_df