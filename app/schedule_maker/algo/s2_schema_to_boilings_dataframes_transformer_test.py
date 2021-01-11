import os
os.environ['environment'] = 'interactive'

from app.schedule_maker import mark_consecutive_groups
from app.schedule_maker.algo.s1_boiling_group_to_schema_transformer import BoilingGroupToSchemaTransformer
from app.schedule_maker.algo.s2_schema_to_boilings_dataframes_transformer import SchemaToBoilingsDataFramesTransformer

import warnings
warnings.filterwarnings('ignore')


def test():
    from app.schedule_maker import read_boiling_plan
    df = read_boiling_plan(r"../data/sample_boiling_plan.xlsx")
    mark_consecutive_groups(df, 'boiling', 'boiling_group')
    boiling_group_df = df[df['boiling_group'] == 2]

    boilings_meltings, packings, melting_speed = BoilingGroupToSchemaTransformer()(boiling_group_df)
    boilings_dataframes = SchemaToBoilingsDataFramesTransformer()(boilings_meltings, packings, melting_speed)
    print(boilings_dataframes)


if __name__ == '__main__':
    test()