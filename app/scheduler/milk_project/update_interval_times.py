from app.scheduler.milk_project.parser_new import parse_schedule


def update_interval_times(schedule_wb, boiling_plan_df):
    schedule_info = parse_schedule((schedule_wb, "Расписание"))

    if len(boiling_plan_df) == 0:
        return boiling_plan_df

    boilings = schedule_info.get("milk_project_boilings", [])
    boilings = list(sorted(boilings, key=lambda b: b["interval"][0]))
    boiling_plan_df["start"] = ""
    boiling_plan_df["finish"] = ""
    for i, (batch_id, grp) in enumerate(boiling_plan_df.groupby("absolute_batch_id")):
        boiling_plan_df.loc[grp.index, "start"] = boilings[i]["interval_time"][0]
        boiling_plan_df.loc[grp.index, "finish"] = boilings[i]["interval_time"][1]
    return boiling_plan_df
