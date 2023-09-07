import inspect

from inspect import FrameInfo
from pathlib import Path
from pprint import pprint

from app.lessmore.utils.get_frame_path.test_get_frame_path.test_get_frame_path import test_get_frame_path
from app.lessmore.utils.tested import tested


@tested(tests=[test_get_frame_path])  # NOTE: DECORATOR ADDS ONE FRAME DEPTH, used below when adding 2
def get_frame_path(
    frame_num: int,  # 0 - current frame, 1 - parent frame, ...
) -> Path:
    # - Get the current frame

    current_frame = inspect.currentframe()

    # - Get the frame
    caller_frame: FrameInfo = inspect.getouterframes(current_frame)[
        frame_num + 2
    ]  # 0: tested, 1: get_frame_path, 2: caller, ...

    # - Extract the file name from the frame

    return Path(caller_frame.filename)


def get_parent_frame_path():
    return get_frame_path(frame_num=2)
