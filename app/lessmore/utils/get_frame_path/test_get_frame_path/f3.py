from pathlib import Path

from app.lessmore.utils.get_frame_path.test_get_frame_path.f2 import f2


def f3(frame_num: int) -> Path:
    return f2(frame_num=frame_num)
