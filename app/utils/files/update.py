from app.imports.runtime import *
from app.utils.files.utils import create_if_not_exists


def update_data_structure(folder):
    boiling_dir = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        folder
    )
    boiling_filenames = os.listdir(boiling_dir)
    for filename in boiling_filenames:
        date = filename.split('.')[0].split(' ')[0]
        new_boiling_dir = os.path.join(flask.current_app.config["DYNAMIC_DIR"], date, folder)
        create_if_not_exists(new_boiling_dir)
        shutil.move(os.path.join(boiling_dir, filename), os.path.join(new_boiling_dir, filename))

