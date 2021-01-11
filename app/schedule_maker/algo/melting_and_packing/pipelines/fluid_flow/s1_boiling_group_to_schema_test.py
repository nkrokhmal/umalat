import os
os.environ['environment'] = 'interactive'

from app.schedule_maker import mark_consecutive_groups
from app.schedule_maker.algo import *

import warnings
warnings.filterwarnings('ignore')

def test():
    df = read_boiling_plan(r"../data/sample_boiling_plan.xlsx")
    mark_consecutive_groups(df, 'boiling', 'boiling_group')
    boiling_group_df = df[df['boiling_group'] == 2]
    transformer = BoilingGroupToSchemaTransformer()
    boilings_meltings, packings, melting_speed = transformer(boiling_group_df)
    print(boilings_meltings, packings, melting_speed)

if __name__ == '__main__':
    test()