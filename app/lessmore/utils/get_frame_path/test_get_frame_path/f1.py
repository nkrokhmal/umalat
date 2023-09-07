from pathlib import Path

from app.lessmore.utils.get_frame_path.get_frame_path import get_frame_path


def f1(frame_num: int) -> Path:
    return get_frame_path(frame_num=frame_num)
