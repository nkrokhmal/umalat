# fmt: off

from app.imports.runtime import *

from app.scheduler.butter.algo.boilings import *
from app.models import *


def make_schedule(boiling_plan_df):
    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()

    # todo soon: del (after butterboiling is fixed (probably too many boilings somewhere)
    boiling_plan_df = boiling_plan_df[boiling_plan_df['boiling'] != cast_model(ButterBoiling, 8)]

    sample_row = boiling_plan_df.iloc[0]
    line = sample_row['boiling'].line

    m.row('preparation', size=line.preparing_time // 5)
    for boiling_id, grp in boiling_plan_df.groupby("boiling_id"):
        m.row(make_boiling(grp))
    m.row('displacement', size=line.displacement_time // 5)

    # todo soon: take from line model
    m.row("cleaning", size=20)
    return m.root
