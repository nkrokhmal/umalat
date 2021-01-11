import os
os.environ['environment'] = 'interactive'

from config import basedir
from app.schedule_maker.algo import BoilingGroupToSchemaTransformer
from app.schedule_maker import mark_consecutive_groups

import warnings
warnings.filterwarnings('ignore')

def test():
    from app.schedule_maker import read_boiling_plan
    df = read_boiling_plan(os.path.join(basedir, "app/schedule_maker/data/sample_boiling_plan.xlsx"))
    mark_consecutive_groups(df, 'boiling', 'boiling_group')
    boiling_group_df = df[df['boiling_group'] == 2]
    transformer = BoilingGroupToSchemaTransformer()
    boilings_meltings, packings, melting_speed = transformer(boiling_group_df)
    print(boilings_meltings, packings, melting_speed)

if __name__ == '__main__':
    test()