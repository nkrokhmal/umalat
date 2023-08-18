def test_batch():
    fns = glob.glob(config.abs_path("app/data/static/samples/outputs/by_department/mascarpone/*.xlsx"))
    fns = [fn for fn in fns if "$" not in fn]
    for i, fn in enumerate(tqdm(fns, desc=lambda v: v)):
        _test(fn, open_file=False, prefix=str(i))


def _test(fn, *args, **kwargs):
    lazy_tester.configure_function_path()
    warnings.filterwarnings("ignore")
    lazy_tester.configure(local_path=os.path.basename(fn))

    outputs = parse_schedule((fn, "Расписание"))

    lazy_tester.log(outputs)
    lazy_tester.assert_logs()


if __name__ == "__main__":
    configure_loguru(level="DEBUG")
    test_batch()
