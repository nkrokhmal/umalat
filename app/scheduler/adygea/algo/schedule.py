# fmt: off

from app.imports.runtime import *

from app.scheduler.adygea.algo.boilings import *
from app.scheduler.time import *
from app.models import *


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=30)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1['collecting'], b2['collecting'])
        if b1.props['boiler_num'] == b2.props['boiler_num']:
            validate_disjoint_by_axis(b1, b2)

    @staticmethod
    def validate__boiling__lunch(b1, b2):
        if b1.props['boiler_num'] >> 1 == b2.props['pair_num']: # 0, 1 -> 0, 2, 3 -> 1
            validate_disjoint_by_axis(b1, b2, distance=2)

    @staticmethod
    def validate__lunch__boiling(b1, b2):
        if b2.props['boiler_num'] >> 1 == b1.props['pair_num']: # 0, 1 -> 0, 2, 3 -> 1
            validate_disjoint_by_axis(b1, b2)


def _make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00', lunch_boiling_ids=None):
    lunch_boiling_ids = lunch_boiling_ids or []
    assert len(lunch_boiling_ids) in [0, 2] # no lunches or two lunches for two teams

    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()

    cur_boiler_num = 0
    cur_boiling_id = boiling_plan_df['boiling_id'].iloc[0] + first_boiling_id - 1
    for i, row in boiling_plan_df.iterrows():
        for _ in range(row['n_baths']):
            boiling = make_boiling(row['boiling'], boiling_id=cur_boiling_id, boiler_num=cur_boiler_num)
            push(m.root, boiling, push_func=AxisPusher(start_from='last_beg', start_shift=-30), validator=Validator())
            cur_boiler_num = (cur_boiler_num + 1) % 4

            for pair_num, lunch_boiling_id in enumerate(lunch_boiling_ids):
                if lunch_boiling_id == cur_boiling_id:
                    push(m.root, make_lunch(pair_num=pair_num), push_func=AxisPusher(start_from='last_beg'), validator=Validator())

            cur_boiling_id += 1

    for i, r in enumerate([range(0, 2), range(2, 4)]):
        range_boilings = [boiling for boiling in m.root['boiling', True] if boiling.props['boiler_num'] in r]
        end = max(boiling.y[0] for boiling in range_boilings)
        m.row(make_cleaning(pair_num=i), x=end + 1, push_func=add_push)

    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root


def make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00'):
    no_lunch_schedule = _make_schedule(boiling_plan_df, first_boiling_id, start_time)

    lunch_boiling_ids = []
    for i, r in enumerate([range(0, 2), range(2, 4)]):
        range_boilings = [boiling for boiling in no_lunch_schedule['boiling', True] if boiling.props['boiler_num'] in r]

        # find lunch times
        for b1, b2, b3 in utils.iter_sequences(range_boilings, 3, method='any'):
            if not b2:
                continue

            if cast_time(b2.y[0]) >= '00:12:00':
                lunch_boiling_ids.append(b2.props['boiling_id'])
                break
    return _make_schedule(boiling_plan_df, first_boiling_id, start_time, lunch_boiling_ids=lunch_boiling_ids)
