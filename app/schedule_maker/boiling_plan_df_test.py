import os
os.environ['environment'] = 'interactive'

from app.schedule_maker.boiling_plan_df import read_boiling_plan


def test_read_boiling_plan():
    print(read_boiling_plan('data/sample_boiling_plan.xlsx'))


if __name__ == '__main__':
    test_read_boiling_plan()