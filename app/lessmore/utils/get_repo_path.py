from pathlib import Path

from app.lessmore.utils.get_frame_path.get_frame_path import get_parent_frame_path


def get_repo_path() -> Path:
    # - Find nearest .git folder path

    current_path = Path(get_parent_frame_path()).parent  # move from utils to current repo

    while True:
        if (current_path / ".git").exists():
            return current_path

        if current_path.parent == current_path:
            raise Exception("No .git folder found")

        current_path = current_path.parent


def test():
    assert get_repo_path().name == "lessmore"


if __name__ == "__main__":
    test()
