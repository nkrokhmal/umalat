import subprocess


def get_last_commit_name():
    process = subprocess.Popen(['git', 'log', 'master', '--format=%B', '-1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    last_commit_name = str(process.stdout.read()).lower()

    print(last_commit_name)

    if "--no-tests" in last_commit_name or "--no-test" in last_commit_name:
        # todo: fast tests
        pass
    else:
        from tests.runners.runner import run_test

        run_test("tests")


if __name__ == "__main__":
    get_last_commit_name()
