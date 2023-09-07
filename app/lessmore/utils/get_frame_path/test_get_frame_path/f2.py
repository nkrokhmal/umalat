from pathlib import Path

from app.lessmore.utils.get_frame_path.test_get_frame_path.f1 import f1


def f2(frame_num: int) -> Path:
    return f1(frame_num=frame_num)
