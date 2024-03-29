import os

import notifiers
import py

from pytest import ExitCode

from config import basedir, configs


def run_test(local_path, config_name="test", notify_if_failed=True):
    os.chdir(basedir)

    config = configs[config_name]

    if notify_if_failed and not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        raise Exception("Telegram credentials not specified.")

    # run test and stop at first failure (-x option)
    code = py.test.cmdline.main([os.path.join(basedir, local_path), "-x"])

    if code == ExitCode.TESTS_FAILED:
        if notify_if_failed:
            telegram = notifiers.get_notifier("telegram")
            telegram.notify(
                message=f"Failed to run tests under: {local_path}",
                token=config.TELEGRAM_BOT_TOKEN,
                chat_id=config.TELEGRAM_CHAT_ID,
            )
        raise Exception(f"Failed to run tests under: {local_path}")
