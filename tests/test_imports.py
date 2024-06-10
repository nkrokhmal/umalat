import fnmatch
import glob
import importlib.util
import os
import sys

from functools import partial
from typing import Callable, Union

import tqdm

from loguru import logger


# - Utils


def _import_module(path):
    spec = importlib.util.spec_from_file_location(
        "module.name",
        path,
    )
    foo = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = foo
    spec.loader.exec_module(foo)


def list_files(
    path: str,
    pattern: Union[None, str, Callable] = None,
    recursive: bool = True,
):
    # - Get list of files

    if not recursive:
        filenames = [filename for filename in os.listdir(path) if os.path.isfile(filename)]
    else:
        if os.path.isfile(path):
            filenames = [path]
        else:
            # glob.glob('**/*') is slower 2.5 times than simple os.walk. It also returns directories
            filenames = []
            for root, dirs, files in os.walk(path):
                filenames += [os.path.join(root, filename) for filename in files]

    # - Set filter for string pattern

    if isinstance(pattern, str):
        pattern = partial(fnmatch.fnmatch, pat=pattern)

    # - Filter

    if pattern:
        filenames = [filename for filename in filenames if pattern(filename)]

    # - Return

    return filenames


# - Test_imports


def test_imports(path: str):
    # import all files and make sure there is no import errors
    for fn in tqdm.tqdm(
        list_files(
            path,
            pattern=lambda filename: filename.endswith(".py")
            and ".venv" not in filename
            and "__pycache__" not in filename
            and "archive" not in filename,
        )
    ):
        _import_module(fn)


if __name__ == "__main__":
    logger.info("Start testing imports")
    test_imports("../app/scheduler")
    # test_imports("../app/main")
