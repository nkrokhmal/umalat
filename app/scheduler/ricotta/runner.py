def run_ricotta(
    boiling_plan_fn=None,
    schedule=None,
    open_file=False,
    start_time=None,
    first_batch_id=1,
    path="outputs/",
    prefix="",
):
    makedirs(path)
    boiling_plan_df = read_boiling_plan(boiling_plan_fn, first_batch_ids={"ricotta": first_batch_id})
    start_time = start_time or "07:00"
    if not schedule:
        schedule = make_schedule(boiling_plan_df, start_time=start_time)

    try:
        frontend = wrap_frontend(schedule)
    except Exception as e:
        raise Exception("Ошибка при построении расписания")
    res = submit_schedule("рикотта", schedule, frontend, prefix, STYLE, path=path, open_file=open_file)
    res["boiling_plan_df"] = boiling_plan_df
    return res
