def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, "Расписание"))
    boiling_plan_df["interval_time"] = None

    interval_times = {}

    for boiling in schedule_info["boilings"]:
        interval_times[boiling["boiling_id"]] = boiling["interval_time"]

    boiling_plan_df["start"] = boiling_plan_df["absolute_batch_id"].apply(
        lambda batch_id: interval_times.get(batch_id, [None, None])[0]
    )
    boiling_plan_df["finish"] = boiling_plan_df["absolute_batch_id"].apply(
        lambda batch_id: interval_times.get(batch_id, [None, None])[1]
    )
    return boiling_plan_df
