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
    transformer = BoilingGroupToSchema()
    boilings_meltings, packings = transformer(boiling_group_df)
    print(boilings_meltings, packings)

# todo: del
def test2():
    df = read_boiling_plan(r"C:\Users\Mi\Desktop\code\git\2020.10-umalat\umalat\research\akadaner\Реальные расписания\2021-01-19 План по варкам.xlsx")
    boiling_group_df = df[df['batch_id'] == 1]
    print(boiling_group_df)
    transformer = BoilingGroupToSchema()
    boilings_meltings, packings = transformer(boiling_group_df)
    print(boilings_meltings, packings)

if __name__ == '__main__':
    test2()