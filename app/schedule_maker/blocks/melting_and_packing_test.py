import os
import time
os.environ['environment'] = 'interactive'

from app.schedule_maker.dataframes import read_boiling_plan
from app.schedule_maker.blocks import make_melting_and_packing_basic


def test_melting_and_packing_basic_single():
    from app.schedule_maker.dataframes import read_boiling_plan
    boiling_plan_df = read_boiling_plan(r"../data/sample_boiling_plan.xlsx")
    boiling_plan = boiling_plan_df[boiling_plan_df['batch_id'] == 81]
    block = make_melting_and_packing_basic(boiling_plan)
    print(block.tabular())


def test_melting_and_packing_basic_many():
    from app.schedule_maker.dataframes import read_boiling_plan
    boiling_plan_df = read_boiling_plan(r"../data/sample_boiling_plan.xlsx")
    for batch_id, grp in boiling_plan_df.groupby('batch_id'):
        print('Processing batch_id', batch_id)
        block = make_melting_and_packing_basic(grp)
        print(block.tabular())


if __name__ == '__main__':
    test_melting_and_packing_basic_single()
    test_melting_and_packing_basic_many()