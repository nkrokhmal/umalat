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
    boiling_group_df = df[df['boiling_group'] == 2]
    print(boiling_group_df)
    boiling_model = boiling_group_df.iloc[0]['boiling']
    boilings_meltings, packings = BoilingGroupToSchema()(boiling_group_df)
    boilings_dataframes = SchemaToBoilingsDataframes()(boilings_meltings, packings, boiling_model.line.melting_speed, round=False)
    for boiling_dataframes in boilings_dataframes:
        print(boiling_dataframes['meltings'])
        print(boiling_dataframes['coolings'])
        for packing_team_id, df in boiling_dataframes['packings'].items():
            print(df)
        print()

# todo: del
def test2():
    df = read_boiling_plan(r"C:\Users\Mi\Desktop\code\git\2020.10-umalat\umalat\research\akadaner\Реальные расписания\2021-01-19 План по варкам.xlsx")
    boiling_group_df = df[df['batch_id'] == 1]
    print(boiling_group_df)
    boiling_model = boiling_group_df.iloc[0]['boiling']
    boilings_meltings, packings = BoilingGroupToSchema()(boiling_group_df)
    boilings_dataframes = SchemaToBoilingsDataframes()(boilings_meltings, packings, boiling_model.line.melting_speed, round=True)
    for boiling_dataframes in boilings_dataframes:
        print(boiling_dataframes['meltings'])
        print(boiling_dataframes['coolings'])
        for packing_team_id, df in boiling_dataframes['packings'].items():
            print(df)
        print()


if __name__ == '__main__':
    test2()