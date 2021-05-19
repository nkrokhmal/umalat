import py
import os
from config import basedir
from pytest import ExitCode


def run_test(local_path):
    code = py.test.cmdline.main([os.path.join(basedir, local_path)])

    if code == ExitCode.TESTS_FAILED:
        raise Exception(f"Failed to run tests under: {local_path}")
