def submit_schedule(
    name,
    schedule,
    frontend,
    prefix,
    style,
    template_wb=None,
    path=None,
    open_file=False,
    split_file=False,
):
    makedirs(path)

    if path:
        with code("Dump schedule as pickle file"):
            base_fn = f"Расписание {name}.pickle"
            if prefix:
                base_fn = prefix + " " + base_fn
            output_pickle_fn = os.path.join(path, base_fn)
            if split_file:
                output_pickle_fn = SplitFile(output_pickle_fn).get_new()

            with open(output_pickle_fn, "wb") as f:
                pickle.dump(schedule.to_dict(), f)

    output_fn = None
    if path:
        with code("Generate output fn"):
            base_fn = f"Расписание {name}.xlsx"
            if prefix:
                base_fn = prefix + " " + base_fn
            output_fn = os.path.join(path, base_fn)

            if split_file:
                output_fn = SplitFile(output_fn).get_new()

    workbook = draw_excel_frontend(frontend, open_file=open_file, fn=output_fn, style=style, wb=template_wb)

    return {"schedule": schedule, "frontend": frontend, "workbook": workbook}
