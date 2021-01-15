import os
os.environ['environment'] = 'interactive'

from config import basedir
from app.schedule_maker import mark_consecutive_groups
from app.schedule_maker.algo import *

import warnings
warnings.filterwarnings('ignore')


def test():
    df = read_boiling_plan(os.path.join(basedir, "app/schedule_maker/data/sample_boiling_plan.xlsx"))
    mark_consecutive_groups(df, 'boiling', 'boiling_group')
    boiling_group_df = df[df['boiling_group'] == 1]

    for boiling in make_flow_water_boilings(boiling_group_df, start_from_id=1):
        print(boiling)

if __name__ == '__main__':
    test()