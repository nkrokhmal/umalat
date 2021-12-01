# fmt: off

from app.imports.runtime import *

from app.scheduler.adygea.algo.boilings import *
from app.scheduler.time import *
from app.models import *


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=30)

    @staticmethod
    def validate__preparation__boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__boiling__boiling(b1, b2):
        validate_disjoint_by_axis(b1['collecting'], b2['collecting'])
        if b1.props['boiler_num'] == b2.props['boiler_num']:
            validate_disjoint_by_axis(b1, b2)

    @staticmethod
    def validate__boiling__lunch(b1, b2):
        if b1.props['boiler_num'] >> 1 == b2.props['pair_num']: # 0, 1 -> 0, 2, 3 -> 1
            validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__boiling(b1, b2):
        if b2.props['boiler_num'] >> 1 == b1.props['pair_num']: # 0, 1 -> 0, 2, 3 -> 1
            validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__lunch__lunch(b1, b2):
        pass


def _make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00', prepare_start_time='07:00', lunch_times=None):
    lunch_times = lunch_times or []
    lunch_times = list(lunch_times)
    assert len(lunch_times) in [0, 2] # no lunches or two lunches for two teams

    adygea_line = cast_model(AdygeaLine, 7)

    local_start_t = cast_t(start_time) - cast_t(prepare_start_time)
    normed_lunch_times = [cast_time(cast_t(lt) - cast_t(prepare_start_time)) for lt in lunch_times]

    m = BlockMaker("schedule")
    m.row(make_preparation(adygea_line.preparation_time // 5), push_func=add_push)

    boiling_plan_df = boiling_plan_df.copy()
    adygea_cleaning = cast_model(Washer, 'adygea_cleaning')

    cur_boiler_num = 0
    cur_boiling_id = boiling_plan_df['boiling_id'].iloc[0] + first_boiling_id - 1
    for i, row in boiling_plan_df.iterrows():
        for _ in range(row['n_baths']):
            boiling = make_boiling(row['boiling'], boiling_id=cur_boiling_id, boiler_num=cur_boiler_num)
            push(m.root, boiling, push_func=AxisPusher(start_from='last_beg', start_shift=-30, min_start=local_start_t), validator=Validator())
            cur_boiler_num = (cur_boiler_num + 1) % 4

            with code('Push lunch if needed'):
                if normed_lunch_times:
                    pair_num = cur_boiler_num % 2
                    if normed_lunch_times[pair_num] and cast_time(boiling.y[0]) >= normed_lunch_times[pair_num]:
                        push(m.root, make_lunch(size=adygea_line.lunch_time // 5, pair_num=pair_num), push_func=AxisPusher(start_from=cast_t(normed_lunch_times[pair_num]), min_start=local_start_t), validator=Validator())
                        normed_lunch_times[pair_num] = None # pushed lunch, nonify lunch time

            cur_boiling_id += 1

    with code('Push lunches if not pushed yet'):
        for pair_num, lunch_time in enumerate(normed_lunch_times):
            if lunch_time:
                push(m.root, make_lunch(size=adygea_line.lunch_time // 5, pair_num=pair_num), push_func=AxisPusher(start_from=cast_t(lunch_time), min_start=local_start_t), validator=Validator())

    with code('Cleaning'):
        last_boilings = [utils.iter_get([boiling for boiling in m.root['boiling', True] if boiling.props['boiler_num'] == boiler_num], -1) for boiler_num in range(4)]
        last_boilings = [b for b in last_boilings if b]
        cleaning_start = min(b.y[0] for b in last_boilings)
        if len(m.root['lunch', True]) > 0:
            cleaning_start = max(cleaning_start, min(b.y[0] for b in m.root['lunch', True]))
        m.row(make_cleaning(size=adygea_cleaning.time // 5), x=cleaning_start, push_func=add_push)

    m.root.props.update(x=(cast_t(prepare_start_time), 0))
    return m.root


def make_schedule(boiling_plan_df, first_boiling_id=1, start_time='07:00', prepare_start_time='07:00'):
    no_lunch_schedule = _make_schedule(boiling_plan_df,
                                       first_boiling_id,
                                       start_time=start_time,
                                       prepare_start_time=prepare_start_time)

    need_a_break = no_lunch_schedule.y[0] - no_lunch_schedule.x[0] >= 8 * 12 # work more than 8 hours

    if not need_a_break:
        # no lunch in these cases
        lunch_times = []
        # print('No lunch needed')
    else:
        lunch_times = []
        for i, r in enumerate([range(0, 2), range(2, 4)]):
            range_boilings = [boiling for boiling in no_lunch_schedule['boiling', True] if boiling.props['boiler_num'] in r]

            def find_first_after(time):
                for b1, b2, b3 in utils.iter_sequences(range_boilings, 3, method='any'):
                    if not b2:
                        continue

                    if cast_time(b2.y[0]) >= time:
                        if b3 and b1:
                            if b2.y[0] - b1.y[0] >= b3.y[0] - b2.y[0]:
                                # wait for next boiling and make lunch
                                return cast_time(b3.y[0])
                            else:
                                # make lunch now
                                return cast_time(b2.y[0])
                        else:
                            # make lunch now
                            return cast_time(b2.y[0])

                raise Exception('Did not find lunch time')

            working_interval = cast_interval(no_lunch_schedule.x[0], no_lunch_schedule.y[0])
            lunch_interval = cast_interval(cast_t('12:00'), cast_t('14:30'))

            if lunch_interval.upper - working_interval.lower <= working_interval.upper - lunch_interval.lower:
                # lunch is closer to the start
                if lunch_interval.upper - working_interval.lower >= 2 * 12:
                    lunch_times.append(find_first_after('00:13:30'))
                    # print(1, lunch_times)
                    continue

            else:
                # lunch is close to the end
                if working_interval.upper - lunch_interval.lower >= 2 * 12:
                    lunch_times.append(find_first_after('00:12:00'))
                    # print(2, lunch_times)
                    continue
                elif working_interval.upper - lunch_interval.lower >= 0:
                    # less than two hours till end - still possibly need a break
                    if need_a_break:
                        if lunch_interval.lower - working_interval.lower <= 7 * 12:
                            # work around 7 hours
                            lunch_times.append(find_first_after('00:12:00'))
                            # print(3, lunch_times)
                            continue

            if need_a_break:
                lunch_times.append(find_first_after(cast_time(no_lunch_schedule.x[0] + 6 * 12)))
                # print(4, lunch_times)
                continue

    return _make_schedule(boiling_plan_df,
                          first_boiling_id,
                          start_time=start_time,
                          prepare_start_time=prepare_start_time,
                          lunch_times=lunch_times)
