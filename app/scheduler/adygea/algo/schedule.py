# fmt: off

from app.imports.runtime import *

from app.scheduler.adygea.algo.boilings import *
from app.scheduler.time import *
from app.models import *


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=3)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1['collecting'], b2['collecting'])
        if b1.props['boiler_num'] == b2.props['boiler_num']:
            validate_disjoint_by_axis(b1, b2)


def make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00'):
    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()
    boiling_plan_df["boiling_id"] += first_boiling_id - 1

    cur_boiler_num = 0
    for i, row in boiling_plan_df.iterrows():
        for _ in range(row['n_baths']):
            boiling = make_boiling(row['boiling'], boiler_num=cur_boiler_num)
            push(m.root, boiling, push_func=AxisPusher(start_from='last_beg'), validator=Validator())
            cur_boiler_num = (cur_boiler_num + 1) % 4

    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root
