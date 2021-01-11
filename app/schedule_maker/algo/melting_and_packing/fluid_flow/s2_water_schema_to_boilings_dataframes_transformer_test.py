import os
os.environ['environment'] = 'interactive'

from config import basedir
from app.schedule_maker import mark_consecutive_groups
from app.schedule_maker.algo import *

import warnings
warnings.filterwarnings('ignore')


def test():
    from app.schedule_maker import read_boiling_plan
    df = read_boiling_plan(os.path.join(basedir, "app/schedule_maker/data/sample_boiling_plan.xlsx"))
    mark_consecutive_groups(df, 'boiling', 'boiling_group')
    boiling_group_df = df[df['boiling_group'] == 2]

    boilings_meltings, packings, melting_speed = BoilingGroupToSchemaTransformer()(boiling_group_df)
    boilings_dataframes = SchemaToBoilingsDataFramesTransformer()(boilings_meltings, packings, melting_speed)
    print(boilings_dataframes)


if __name__ == '__main__':
    test()