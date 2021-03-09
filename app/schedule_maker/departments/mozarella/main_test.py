import os

from utils_ak.loguru import configure_loguru_stdout


def test():
    configure_loguru_stdout("INFO")
    os.environ["environment"] = "interactive"
    from app.schedule_maker.departments.mozarella.main import main
    from config import DebugConfig

    fn = DebugConfig.abs_path("app/data/inputs/sample_boiling_plan.xlsx")
    main(fn, optimize=False, open_file=True)


def test_optimize():
    configure_loguru_stdout("INFO")
    os.environ["environment"] = "interactive"
    from app.schedule_maker.departments.mozarella.main import main
    from config import DebugConfig

    fn = DebugConfig.abs_path("app/data/inputs/sample_boiling_plan.xlsx")
    main(fn, optimize=True, open_file=False)


if __name__ == "__main__":
    test()
