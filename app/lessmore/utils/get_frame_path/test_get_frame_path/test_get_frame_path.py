def test_get_frame_path():
    from app.lessmore.utils.get_frame_path.test_get_frame_path.f3 import f3

    assert f3(frame_num=0).name == "f1.py"
    assert f3(frame_num=1).name == "f2.py"
    assert f3(frame_num=2).name == "f3.py"
    assert f3(frame_num=3).name == "test_get_frame_path.py"


if __name__ == "__main__":
    test_get_frame_path()
