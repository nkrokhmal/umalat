def test_batch():
    fns = glob.glob(config.abs_path("app/data/static/samples/inputs/by_department/mascarpone/*.xlsx"))
    fns = [fn for fn in fns if "$" not in fn]

    for i, fn in enumerate(tqdm(fns, desc=lambda fn: fn)):
        _test(fn, open_file=False, prefix=str(i))


def _test(fn, *args, **kwargs):
    configure_loguru_stdout("INFO")
    lazy_tester.configure_function_path()
    lazy_tester.configure(local_path=os.path.basename(fn))
    outputs = run_mascarpone(fn, *args, **kwargs)
    lazy_tester.log(outputs["schedule"])
    lazy_tester.assert_logs(reset=False)


if __name__ == "__main__":
    # _test(
    #     config.abs_path(
    #         "app/data/static/samples/inputs/by_department/mascarpone/План по варкам маскарпоне 1 новый.xlsx"
    #     ),
    #     open_file=True,
    # )

    test_batch()
