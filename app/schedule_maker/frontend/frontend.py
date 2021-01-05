import openpyxl
import pandas as pd

from app.schedule_maker.drawing import *
from app.schedule_maker.frontend.style import *
from utils_ak.interactive_imports import *


def format_label(label_weights):
    label_weights = remove_neighbor_duplicates(label_weights)
    cur_label = None
    values = []
    for label, weight in label_weights:
        s = ''
        if label != cur_label:
            s += label + ' '
            cur_label = label

        # todo: make properly, this if-else if because of rubber. Should be something better
        if weight:
            if str(weight / 1000) == '0.03':
                s += 'палочки'
            else:
                s += str(weight / 1000)
        else:
            s += 'терка'
        values.append(s)
    return '/'.join(values)


def make_header(start_time='01:00'):
    maker, make = init_block_maker('header', axis=1)

    with make('header', size=(0, 1), index_width=3):
        make(size=(1, 1), text='График наливов', push_func=add_push)
        for i in range(288):
            cur_time = cast_time(i + cast_t(start_time))
            if cur_time[-2:] == '00':
                make(x=(1 + i, 0), size=(1,1), text=str(int(cur_time[:2])), color=(218, 150, 148), text_rotation=90, push_func=add_push)
            else:
                make(x=(1 + i, 0), size=(1,1), text=cur_time[-2:], color=(204, 255, 255), text_rotation=90, push_func=add_push)
    return maker.root['header']


def make_cheese_makers(schedule, rng):
    maker, make = init_block_maker('cheese_makers',
                                   axis=1)

    for i in rng:
        with make(f'cheese_maker', is_parent_node=True):
            with make('header', index_width=0, beg_time='00:00', push_func=add_push):
                make('template', x=(1, 0), size=(3, 2), text=f'Сыроизготовитель №1 Poly {i + 1}', color=(183, 222, 232), push_func=add_push)

            for boiling in schedule.iter({'class': 'boiling', 'pouring_line': str(i)}):
                boiling_model = boiling.props['boiling_model']

                # todo: make properly
                boiling_volume = 8000

                # [cheesemakers.boiling_params]
                boiling_label = '{} {} {} {}кг'.format(boiling_model.percent, boiling_model.ferment, '' if boiling_model.is_lactose else 'безлактозная', boiling_volume)

                with make('pouring_block', boiling_label=boiling_label,
                          boiling_id=boiling.props['boiling_id'], x=(boiling['pouring'].x[0], 0),
                          push_func=add_push, axis=1):
                    with make():
                        make('termizator', size=(boiling['pouring']['first']['termizator'].size[0], 1))
                        make('pouring_name', size=(boiling['pouring'].size[0] - boiling['pouring']['first']['termizator'].size[0], 1), boiling_label=boiling_label)
                    with make():
                        make('pouring_and_fermenting', size=(boiling['pouring']['first']['termizator'].size[0] + boiling['pouring']['first']['fermenting'].size[0], 1), push_func=add_push)
                        make('soldification', size=(boiling['pouring']['first']['soldification'].size[0], 1))
                        make('cutting', size=(boiling['pouring']['first']['cutting'].size[0], 1))
                        make('pouring_off', size=(boiling['pouring']['second']['pouring_off'].size[0], 1))
                        make('extra', size=(boiling['pouring']['second']['extra'].size[0], 1))
    return maker.root


def make_cleanings(schedule):
    maker, make = init_block_maker('cleanings_row', axis=1, make_with_copy_cut=True)
    make(schedule['cleanings'])
    for cleaning in listify(maker.root['cleanings']['cleaning']):
        cleaning.props.update({'size': (cleaning.size[0], 2)})
    return maker.root['cleanings']


def make_water_meltings(schedule):
    maker, make = init_block_maker('melting')

    with make('header', beg_time='00:00', push_func=add_push):
        make('template', index_width=0, x=(1, 0), size=(3, 2), text='Линия плавления моцареллы в воде №1', push_func=add_push)

    cur_cooling_line_i = 0
    # n_cooling_lines = 5
    n_cooling_lines = 1
    for boiling in schedule.iter({'class': 'boiling', 'boiling_model': lambda bm: bm.boiling_type == 'water'}):

        # todo: use bffs instead of skus
        # bffs = [melting_process.props['bff'] for melting_process in boiling.iter({'class': 'melting_process'})]
        # form_factor_label = format_label([('', bff.weight) for bff in bffs])

        boiling_skus = []
        for packing in listify(boiling['melting_and_packing']['packing']):
            boiling_skus += [packing_process.props['sku'] for packing_process in packing.iter({'class': 'packing_process'})]
        values = [(sku.form_factor.name, sku.weight_form_factor) for sku in boiling_skus]
        if len(set(v[0] for v in values)) > 1:
            values = [(sku.form_factor.short_name, sku.weight_form_factor) for sku in boiling_skus]
        form_factor_label = format_label(values)

        with make('melting_block', axis=1, boiling_id=boiling.props['boiling_id'], push_func=add_push, form_factor_label=form_factor_label):
            with make('serving_row'):
                make('serving', x=(boiling['melting_and_packing']['melting']['serving'].x[0], 0),
                     size=(boiling['melting_and_packing']['melting']['serving'].size[0], 1), push_func=add_push)

            with make('label_row'):
                make('serving', x=(boiling['melting_and_packing']['melting']['serving'].x[0], 0), size=(boiling['melting_and_packing']['melting']['serving'].size[0], 1), visible=False, push_func=add_push)
                make('melting_label', size=(4, 1))
                make('melting_name', size=(boiling['melting_and_packing']['melting']['meltings'].size[0] - 4, 1), form_factor_label=boiling.props['form_factor_label'])

            with make('melting_row'):
                make('melting_process', x=(boiling['melting_and_packing']['melting']['meltings'].x[0], 0),
                     size=(boiling['melting_and_packing']['melting']['meltings'].size[0], 1), speed=900, push_func=add_push)

            with make('cooling_row', axis=1):
                cooling_lines = [make('cooling_line', size=(0, 1), is_parent_node=True).block for _ in range(n_cooling_lines)]
                for cooling_process in listify(boiling['melting_and_packing']['melting']['coolings']['cooling_process']):
                    for i in range(2):
                        block = maker.create_block('cooling',
                                     size=(cooling_process['start']['cooling'][i].size[0], 1),
                                     x=[cooling_process['start']['cooling'][i].x[0], 0])
                        push(cooling_lines[cur_cooling_line_i % n_cooling_lines], block, push_func=add_push)
                    cur_cooling_line_i += 1
                    # todo: del
                    break
    return maker.root


def make_shifts(start_from, shifts):
    maker, make = init_block_maker('shifts', axis=0, x=[start_from, 0])

    for shift in shifts:
        shift.setdefault('color', (149, 179, 215))
        make('shift', **shift)
    return maker.root


def make_salt_melting(boiling):
    maker, make = init_block_maker('meltings', axis=1)

    # todo: use bffs instead of skus
    # bffs = [melting_process.props['bff'] for melting_process in boiling.iter({'class': 'melting_process'})]
    # form_factor_label = format_label([('', bff.weight) for bff in bffs])

    boiling_skus = []
    for packing in listify(boiling['melting_and_packing']['packing']):
        boiling_skus += [packing_process.props['sku'] for packing_process in packing.iter({'class': 'packing_process'})]
    values = [(sku.form_factor.name, sku.weight_form_factor) for sku in boiling_skus]
    if len(set(v[0] for v in values)) > 1:
        values = [(sku.form_factor.short_name, sku.weight_form_factor) for sku in boiling_skus]
    form_factor_label = format_label(values)

    with make('melting_block', axis=1, boiling_id=boiling.props['boiling_id'], form_factor_label=form_factor_label, push_func=add_push):
        with make('label_row', x=(boiling['melting_and_packing']['melting']['serving'].x[0], 0), push_func=add_push):
            make('melting_label', size=(4, 1), block_front_id=boiling.props['block_front_id'])
            make('melting_name', size=(boiling['melting_and_packing']['melting'].size[0] - 4, 1), form_factor_label=boiling.props['form_factor_label'])

        with make('melting_row'):
            make('serving', x=(boiling['melting_and_packing']['melting']['serving'].x[0], 0),
                 size=(boiling['melting_and_packing']['melting']['serving'].size[0], 1), push_func=add_push)
            make('melting_process',
                 x=(boiling['melting_and_packing']['melting']['meltings'].x[0], 0),
                 size=(boiling['melting_and_packing']['melting']['meltings'].size[0], 1), speed=900, push_func=add_push)
            make('salting', size=(listify(boiling['melting_and_packing']['melting']['coolings']['cooling_process'])[0]['start'].size[0], 1))

        with make('cooling_row'):
            make('salting', x=(listify(boiling['melting_and_packing']['melting']['coolings']['cooling_process'])[0]['start'].x[0], 0),
                 size=(listify(boiling['melting_and_packing']['melting']['coolings']['cooling_process'])[0]['start'].size[0], 1), push_func=add_push)
    return maker.root


def make_salt_meltings(schedule):
    # todo: make dynamic lines
    maker, make = init_block_maker('melting', axis=1, make_with_copy_cut=True)

    n_lines = 5
    melting_lines = [make(f'salt_melting_{i}', size=(0, 3), is_parent_node=True).block for i in range(n_lines)]

    make('template', index_width=0, x=(1, melting_lines[0].x[1]), size=(3, 6), beg_time='00:00', text='Линия плавления моцареллы в рассоле №2', push_func=add_push)

    # todo: hardcode, add empty elements for drawing not to draw melting_line itself

    for i, boiling in enumerate(schedule.iter({'class': 'boiling', 'boiling_model': lambda bm: bm.boiling_type == 'salt'})):
        push(melting_lines[i % n_lines], make_salt_melting(boiling), push_func=add_push)
    return maker.root


def make_packings(schedule, boiling_type):
    maker, make = init_block_maker('packing', axis=1)

    for packing_team_id in range(1, 3):
        with make('packing_team', size=(0, 3), axis=0, is_parent_node=True):
            for boiling in schedule.iter({'class': 'boiling', 'boiling_model': lambda bm: bm.boiling_type == boiling_type}):
                for packing in boiling.iter({'class': 'packing', 'packing_team_id': packing_team_id}):

                    boiling_skus = [packing_process.props['sku'] for packing_process in packing.iter({'class': 'packing_process'})]

                    # todo: take weight from boiling_form_factor
                    values = [(sku.form_factor.name, sku.weight_form_factor) for sku in boiling_skus]
                    if len(set(v[0] for v in values)) > 1:
                        values = [(sku.form_factor.short_name, sku.weight_form_factor) for sku in boiling_skus]
                    form_factor_label = format_label(values)

                    brand_label = '/'.join(remove_neighbor_duplicates([sku.brand_name for sku in boiling_skus]))
                    with make('packing_block', x=(packing.x[0], 0), boiling_id=boiling.props['boiling_id'],
                              push_func=add_push, axis=1, brand_label=brand_label, form_factor_label=form_factor_label):
                        with make():
                            make('packing_label', size=(3, 1))
                            # use different labels for water and salt
                            make('packing_name', size=(packing.size[0] - 3, 1))

                        with make():
                            make('packing_brand', size=(packing.size[0], 1))

                        with make(is_parent_node=True):
                            for conf in packing.iter({'class': 'packing_configuration'}):
                                make('packing_configuration', x=(conf.props['x_rel'][0], 0), size=(conf.size[0], 1), push_func=add_push)
    return maker.root


def draw_excel_frontend(schedule, open_file=False, fn='schedule.xlsx'):
    maker, make = init_block_maker('root', axis=1)

    make('stub', size=(0, 1))

    make(make_header(start_time='01:00'))
    make(make_shifts(5, [{'size': (cast_t('19:00') - cast_t('07:00'), 1), 'text': '1 смена'},
                         {'size': (cast_t('23:55') - cast_t('19:00') + 1 + cast_t('05:30'), 1), 'text': '2 смена'}]))
    make(make_cheese_makers(schedule, range(2)))
    make(make_shifts(5, [{'size': (cast_t('19:00') - cast_t('07:00'), 1), 'text': '1 смена'},
                         {'size': (cast_t('23:55') - cast_t('19:00') + 1 + cast_t('05:30'), 1), 'text': '2 смена'}]))
    make(make_cleanings(schedule))
    make(make_cheese_makers(schedule, range(2, 4)))
    make(make_shifts(5, [{'size': (cast_t('19:05') - cast_t('07:00'), 1), 'text': 'Оператор + Помощник'}]))
    make(make_header(start_time='07:00'))
    make(make_water_meltings(schedule))
    make(make_shifts(5, [{'size': (cast_t('19:05') - cast_t('07:00'), 1), 'text': 'бригадир упаковки + 5 рабочих'}]))
    make(make_packings(schedule, 'water'))
    make(make_shifts(5, [{'size': (cast_t('19:00') - cast_t('07:00'), 1), 'text': '1 смена оператор + помощник'},
                         {'size': (cast_t('23:55') - cast_t('19:00') + 1 + cast_t('05:30'), 1), 'text': '1 оператор + помощник'}]))
    make(make_salt_meltings(schedule))
    make(make_shifts(5, [{'size': (cast_t('19:00') - cast_t('07:00'), 1), 'text': 'Бригадир упаковки +5 рабочих упаковки + наладчик'},
                         {'size': (cast_t('23:55') - cast_t('19:00') + 1 + cast_t('05:30'), 1), 'text': 'бригадир + наладчик + 5 рабочих'}]))
    make(make_packings(schedule, 'salt'))

    wb = draw_schedule(maker.root, STYLE)

    if fn:
        sf = SplitFile(fn)
        fn = sf.get_new()
        wb.save(fn)

        if open_file:
            open_file_in_os(fn)

    return wb