from utils_ak.interactive_imports import *
from app.schedule_maker.time import *
from app.schedule_maker.algo.packing import *
from itertools import product

from app.enum import LineName

class_validator = ClassValidator(window=10)

def validate(b1, b2):
    validate_disjoint_by_axis(b1['pouring']['first']['termizator'], b2['pouring']['first']['termizator'])  # [termizator.basic]

    # cannot make two boilings on same line at the same time
    if b1['pouring'].props['pouring_line'] == b2['pouring'].props['pouring_line']:
        validate_disjoint_by_axis(b1['pouring'], b2['pouring'])

    if b1.props['boiling_model'].line.name == b2.props['boiling_model'].line.name:
        validate_disjoint_by_axis(b1['melting_and_packing']['melting']['meltings'], b2['melting_and_packing']['melting']['meltings'])

        for p1, p2 in product(b1.iter(cls='packing'), b2.iter(cls='packing')):
            if p1.props['packing_team_id'] != p2.props['packing_team_id']:
                continue
            validate_disjoint_by_axis(p1, p2)
class_validator.add('boiling', 'boiling', validate)


def validate(b1, b2):
    boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props['cls'])) # boiling, cleaning
    validate_disjoint_by_axis(boiling['pouring']['first']['termizator'], cleaning)
class_validator.add('boiling', 'cleaning', validate)

def validate(b1, b2):
    boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props['cls'])) # boiling, cleaning
    validate_disjoint_by_axis(cleaning, boiling['pouring']['first']['termizator'])
class_validator.add('cleaning', 'boiling', validate)


def validate(b1, b2):
    boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props['cls'])) # boiling, packing_configuration
    if boiling.props['boiling_model'].line.name != packing_configuration.props['line_name']:
        return

    for p1 in boiling.iter(cls='packing', packing_team_id=packing_configuration.props['packing_team_id']):
        validate_disjoint_by_axis(p1, b2)
class_validator.add('boiling', 'packing_configuration', validate)

def validate(b1, b2):
    boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props['cls'])) # boiling, packing_configuration
    if boiling.props['boiling_model'].line.name != packing_configuration.props['line_name']:
        return

    for p1 in boiling.iter(cls='packing', packing_team_id=packing_configuration.props['packing_team_id']):
        validate_disjoint_by_axis(b1, p1)
class_validator.add('packing_configuration', 'boiling', validate)


def make_termizator_cleaning_block(cleaning_type, **kwargs):
    cleaning_duration = 40 if cleaning_type == 'short' else 80  # todo: take from parameters
    maker, make = init_block_maker('cleaning', size=(cleaning_duration // 5, 0), cleaning_type=cleaning_type, **kwargs)
    return maker.root


def make_schedule(boilings, start_times=None):
    start_times = start_times or {LineName.WATER: '', LineName.SALT: '07:00'}

    maker, make = init_block_maker('schedule')
    schedule = maker.root

    lines_df = pd.DataFrame(index=[LineName.WATER, LineName.SALT], columns=['iter_props', 'start_time', 'boilings_left', 'latest_boiling'])
    lines_df.at[LineName.WATER, 'iter_props'] = [{'pouring_line': str(v)} for v in [0, 1]]
    lines_df.at[LineName.SALT, 'iter_props'] = [{'pouring_line': str(v)} for v in [2, 3]]

    lines_df.at[LineName.WATER, 'start_time'] = cast_time(start_times[LineName.WATER])
    lines_df.at[LineName.SALT, 'start_time'] = cast_time(start_times[LineName.SALT])

    # generate boilings
    lines_df['boilings_left'] = [[], []]
    for line_name in [LineName.WATER, LineName.SALT]:
        lines_df.at[line_name, 'boilings_left'] = [boiling for boiling in boilings if boiling.props['boiling_model'].line.name == line_name]

    lines_df['latest_boiling'] = None

    if not lines_df['start_time'].any():
        raise Exception('Укажите время начала варок')

    def add_one_block_from_line(line_name):
        boiling = lines_df.at[line_name, 'boilings_left'].pop(0)
        if not lines_df.at[line_name, 'latest_boiling']:
            if lines_df.at[line_name, 'start_time']:
                start_from = cast_t(lines_df.at[line_name, 'start_time']) - boiling['melting_and_packing'].x[0]
            else:
                latest_boiling = lines_df[~lines_df['latest_boiling'].isnull()].iloc[0]['latest_boiling']
                start_from = latest_boiling.x[0]
        else:
            start_from = lines_df.at[line_name, 'latest_boiling'].x[0]

        # add configuration if needed
        if lines_df.at[line_name, 'latest_boiling']:
            configuration_blocks = make_configuration_blocks(lines_df.at[line_name, 'latest_boiling'], boiling, maker, line_name)
            for conf in configuration_blocks:
                conf.props.update(line_name=line_name)
                push(schedule, conf, push_func=dummy_push, validator=class_validator, start_from='beg')

        # add cleanings for non-lactose cheese

        if not boiling.props['boiling_model'].is_lactose:
            min_latest_boiling = min(df['latest_boiling'], key=lambda b: b.x[0])
            start_from = min_latest_boiling.x[0]
            latest_boiling = lines_df.at[line_name, 'latest_boiling']
            if latest_boiling and line_name == LineName.SALT and latest_boiling.props['boiling_model'].is_lactose:
                # full cleaning needed
                cleaning = make_termizator_cleaning_block('full', text='Перерыв больше 80 минут')
                push(schedule, cleaning, start_from=start_from, push_func=dummy_push, validator=class_validator)

        push(schedule, boiling, push_func=dummy_push, iter_props=lines_df.at[line_name, 'iter_props'], validator=class_validator, start_from=start_from, max_tries=100)
        lines_df.at[line_name, 'latest_boiling'] = boiling
        return boiling

    while True:
        are_boilings_left = lines_df['boilings_left'].apply(lambda lst: len(lst) > 0)
        if are_boilings_left.sum() == 0:
            # finished
            break
        elif are_boilings_left.sum() == 1:
            line_name = are_boilings_left[are_boilings_left].index[0]

            # start working on 3 line for salt
            lines_df.at[LineName.SALT, 'iter_props'] = [{'pouring_line': str(v)} for v in [1, 2, 3]]

        elif are_boilings_left.sum() == 2:
            df = lines_df[~lines_df['latest_boiling'].isnull()]
            if len(df) == 0:
                line_name = LineName.WATER
            else:
                line_name = max(df['latest_boiling'], key=lambda b: b.x[0]).props['boiling_model'].line.name

            # reverse
            line_name = LineName.WATER if line_name == LineName.SALT else LineName.SALT
        else:
            raise Exception('Should not happen')

        add_one_block_from_line(line_name)

    # add cleanings if necessary
    # todo: refactor
    boilings = list(schedule.iter(cls='boiling'))
    boilings = list(sorted(boilings, key=lambda b: b.x[0]))

    cleanings = list(schedule.iter(cls='cleaning'))

    for a, b in SimpleIterator(boilings).iter_sequences(2):
        rest = b['pouring']['first']['termizator'].x[0] - a['pouring']['first']['termizator'].y[0]

        in_between_cleanings = [c for c in cleanings if a.x[0] <= c.x[0] <= b.x[0]]

        if not in_between_cleanings:
            if 12 <= rest < 18:
                cleaning = make_termizator_cleaning_block('short', text='Перерыв от часа до 80 минут')
                cleaning.props.update(x=(b['pouring']['first']['termizator'].x[0] - cleaning.size[0], 0))
                push(schedule, cleaning, push_func=add_push)

            if rest >= 18:
                cleaning = make_termizator_cleaning_block('full', text='Перерыв больше 80 минут')
                cleaning.props.update(x=(b['pouring']['first']['termizator'].x[0] - cleaning.size[0], 0))
                push(schedule, cleaning, push_func=add_push)

    last_boiling = list(schedule.iter(cls='boiling'))[-1]
    cleaning = make_termizator_cleaning_block('full', x=(last_boiling['pouring']['first']['termizator'].y[0] + 1, 0))  # add five extra minutes
    push(schedule, cleaning, push_func=add_push)

    return schedule