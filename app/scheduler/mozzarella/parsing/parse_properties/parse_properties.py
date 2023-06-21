from app.imports.runtime import *
from app.scheduler.mozzarella import *
from app.scheduler.mozzarella.parsing.parse_properties.fill_properties import fill_properties
from app.scheduler.mozzarella.parsing.parse_properties.parse_schedule_file import parse_schedule_file
from app.scheduler.mozzarella.parsing.parse_properties.prepare_boiling_plan import prepare_boiling_plan
from app.scheduler.mozzarella.properties import *
from app.scheduler.parsing import *
from app.scheduler.parsing_new.parse_time import *

from utils_ak.block_tree import *


def parse_properties(fn):
    parsed_schedule = parse_schedule_file(fn)
    df_bp = read_boiling_plan(fn)
    df_bp = prepare_boiling_plan(parsed_schedule, df_bp)
    props = fill_properties(parsed_schedule, df_bp)
    return props


def test():
    print(parse_properties(r'/Users/arsenijkadaner/FileApps/coding_projects/umalat/app/data/static/samples/outputs/by_department/mozzarella/2023-06-21 Расписание моцарелла.xlsx'))


if __name__ == "__main__":
    utils.configure_loguru(level="DEBUG")
    test()
