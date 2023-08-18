def test_random():
    lazy_tester.configure_function_path()
    lazy_tester.log(generate_random_boiling_plan())
    lazy_tester.assert_logs()


def _test(fn):
    configure_loguru_stdout("INFO")
    lazy_tester.configure_function_path()

    lazy_tester.configure(local_path=os.path.basename(fn))
    boiling_plan_df = read_boiling_plan(fn)
    lazy_tester.log(boiling_plan_df)


def test_samples():
    fns = glob.glob(config.abs_path("app/data/static/samples/inputs/butter/*.xlsx"))
    fns = [fn for fn in fns if "$" not in fn]
    for fn in fns:
        _test(fn)


if __name__ == "__main__":
    test_random()
    test_samples()
