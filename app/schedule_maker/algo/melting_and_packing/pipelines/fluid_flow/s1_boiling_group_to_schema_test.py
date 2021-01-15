import os
os.environ['environment'] = 'interactive'

from app.schedule_maker import mark_consecutive_groups
from app.schedule_maker.algo import *
from config import basedir

import warnings
warnings.filterwarnings('ignore')

def test():
    df = read_boiling_plan(os.path.join(basedir, r"app/schedule_maker/data/sample_boiling_plan.xlsx"))
    mark_consecutive_groups(df, 'boiling', 'boiling_group')
    boiling_group_df = df[df['boiling_group'] == 2]
    transformer = boiling_group_to_schema()
    boilings_meltings, packings = transformer(boiling_group_df)
    print(boilings_meltings, packings)

if __name__ == '__main__':
    test()