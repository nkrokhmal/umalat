# fmt: off

from app.imports.runtime import *

from app.scheduler.butter.algo.boilings import *
from app.scheduler.time import *
from app.models import *


def make_schedule(boiling_plan_df, start_time='07:00'):
    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()

    sample_row = boiling_plan_df.iloc[0]
    line = sample_row['boiling'].line

    m.row('preparation', size=line.preparing_time // 5)
    for boiling_id, grp in boiling_plan_df.groupby("boiling_id"):
        m.row(make_boiling(grp))
    m.row('displacement', size=line.displacement_time // 5)

    # todo next: take from line model
    m.row("cleaning", size=20)

    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root
