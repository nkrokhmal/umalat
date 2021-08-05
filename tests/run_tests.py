import subprocess
import sys
import os


def get_last_commit_name():
    process = subprocess.Popen(['git', 'log', 'master', '--format=%B', '-1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    last_commit_name = str(process.stdout.read()).lower()

    if "--no-tests" in last_commit_name or "--no-test" in last_commit_name:
        # todo: fast tests
        pass
    else:
        from tests.runners.runner import run_test

        run_test("tests")


if __name__ == "__main__":
    current_path = os.getcwd()
    if current_path not in sys.path:
        sys.path.append(current_path)
    get_last_commit_name()
