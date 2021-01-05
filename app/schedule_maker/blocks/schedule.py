from utils_ak.interactive_imports import *
from app.schedule_maker.time import *
from itertools import product


class_validator = ClassValidator(window=10)


def validate(b1, b2):
    validate_disjoint_by_axis(b1['pouring']['first']['termizator'], b2['pouring']['first']['termizator'])  # [termizator.basic]

    # cannot make two boilings on same line at the same time
    if b1['pouring'].props['pouring_line'] == b2['pouring'].props['pouring_line']:
        validate_disjoint_by_axis(b1['pouring'], b2['pouring'])

    if b1.props['boiling_model'].boiling_type == b2.props['boiling_model'].boiling_type:
        validate_disjoint_by_axis(b1['melting_and_packing']['melting']['meltings'], b2['melting_and_packing']['melting']['meltings'])

        for p1, p2 in product(b1.iter({'class': 'packing'}), b2.iter({'class': 'packing'})):
            if p1.props['packing_team_id'] != p2.props['packing_team_id']:
                continue
            validate_disjoint_by_axis(p1, p2)


class_validator.add('boiling', 'boiling', validate)


def validate(b1, b2):
    b1, b2 = list(sorted([b1, b2], key=lambda b: b.props['class'])) # boiling, cleaning
    validate_disjoint_by_axis(b1['pouring']['first']['termizator'], b2)
class_validator.add('boiling', 'cleaning', validate)


def make_termizator_cleaning_block(cleaning_type, **kwargs):
    cleaning_duration = 40 if cleaning_type == 'short' else 80  # todo: take from parameters
    maker, make = init_block_maker('cleaning', size=(cleaning_duration // 5, 0), cleaning_type=cleaning_type, **kwargs)
    return maker.root


def make_schedule(boilings):
    maker, make = init_block_maker('schedule')
    schedule = maker.root

    lines_df = pd.DataFrame(index=['water', 'salt'], columns=['iter_props', 'start_time', 'boilings_left', 'latest_boiling'])
    lines_df.at['water', 'iter_props'] = [{'pouring_line': str(v)} for v in [0, 1]]
    lines_df.at['salt', 'iter_props'] = [{'pouring_line': str(v)} for v in [2, 3]]

    lines_df.at['water', 'start_time'] = '09:50'
    lines_df.at['salt', 'start_time'] = '07:05'

    make('cleanings', push_func=add_push)

    # generate boilings
    lines_df['boilings_left'] = [[], []]
    for boiling_type in ['water', 'salt']:
        lines_df.at[boiling_type, 'boilings_left'] = [boiling for boiling in boilings if boiling.props['boiling_model'].boiling_type == boiling_type]

    lines_df['latest_boiling'] = None

    def add_block(boiling_type):
        boiling = lines_df.at[boiling_type, 'boilings_left'].pop(0)

        if not lines_df.at[boiling_type, 'latest_boiling']:
            start_from = cast_t(lines_df.at[boiling_type, 'start_time']) - boiling['melting_and_packing']['melting'].x[0]
        else:
            start_from = lines_df.at[boiling_type, 'latest_boiling'].x[0]

        push(schedule, boiling, push_func=dummy_push, iter_props=lines_df.at[boiling_type, 'iter_props'], validator=class_validator, start_from=start_from, max_tries=100)

        lines_df.at[boiling_type, 'latest_boiling'] = boiling
        return boiling

    while True:
        are_boilings_left = lines_df['boilings_left'].apply(lambda lst: len(lst) > 0)
        if are_boilings_left.sum() == 0:
            # finished
            break
        elif are_boilings_left.sum() == 1:
            boiling_type = are_boilings_left[are_boilings_left].index[0]
        elif are_boilings_left.sum() == 2:
            df = lines_df[~lines_df['latest_boiling'].isnull()]
            if len(df) == 0:
                boiling_type = 'water'
            else:
                boiling_type = max(df['latest_boiling'], key=lambda b: b.x[0]).props['boiling_model'].boiling_type

            # reverse
            boiling_type = 'water' if boiling_type == 'salt' else 'salt'
        else:
            raise Exception('Should not happen')

        add_block(boiling_type)

    # add cleanings if necessary
    boilings = list(schedule.iter({'class': 'boiling'}))
    boilings = list(sorted(boilings, key=lambda b: b.x[0]))

    for i in range(len(boilings) - 1):
        a, b = list(boilings[i: i + 2])

        rest = b['pouring']['first']['termizator'].x[0] - a['pouring']['first']['termizator'].y[0]

        if 12 <= rest < 18:
            cleaning = make_termizator_cleaning_block('short', text='Перерыв от часа до 80 минут')
            cleaning.props.update({'x': (b['pouring']['first']['termizator'].x[0] - cleaning.size[0], 0)})
            push(schedule['cleanings'], cleaning, push_func=add_push)

        if rest >= 18:
            cleaning = make_termizator_cleaning_block('full', text='Перерыв больше 80 минут')
            cleaning.props.update({'x': (b['pouring']['first']['termizator'].x[0] - cleaning.size[0], 0)})
            push(schedule['cleanings'], cleaning, push_func=add_push)

        # print(b['pouring'][0]['termizator'].y[0], last_full_cleaning_y1)
        # # add full cleaning if working more than 12 hours
        # if b['pouring'][0]['termizator'].y[0] - last_full_cleaning_y1  > cast_t('12:00'):
        #     # [termizator.cleaning.3]
        #     cleaning = make_termizator_cleaning_block('full', x1=b['pouring']['first']['termizator'].y[0], text='Работает больше 12 часов')
        #     push(schedule['cleanings'], cleaning, method='add')

    last_boiling = list(schedule.iter({'class': 'boiling'}))[-1]
    cleaning = make_termizator_cleaning_block('full', x=(last_boiling['pouring']['first']['termizator'].y[0] + 1, 0))  # add five extra minutes
    push(schedule['cleanings'], cleaning, push_func=add_push)

    return schedule