from app.schedule_maker.models import *
from app.schedule_maker.utils import *

from utils_ak.interactive_imports import *


def make_melting_and_packing(boiling_conf, boiling_request, boiling_type,
                             melting_line=None):
    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    with make('melting_and_packing'):
        # packing and melting time
        packing_times = []
        if boiling_type == 'water':
            melting_time = custom_round(850 / boiling_conf.meltings.speed * 60 * 1.3, 5, rounding='ceil')

            # todo: make proper order
            for sku, sku_kg in boiling_request.items():
                packing_speed = min(sku.packing_speed, boiling_conf.meltings.speed)
                packing_times.append(custom_round(sku_kg / packing_speed * 60, 5, rounding='ceil'))
            total_packing_time = sum(packing_times) + (
                        len(packing_times) - 1) * 5  # add time for reconfiguration - 5 minutes between each
            full_melting_time = boiling_conf.meltings.serving_time + melting_time

        elif boiling_type == 'salt':
            # todo: make proper order
            for sku, sku_kg in boiling_request.items():
                packing_times.append(custom_round(sku_kg / sku.packing_speed * 60, 5, rounding='ceil'))
            total_packing_time = sum(packing_times) + (
                        len(packing_times) - 1) * 5  # add time for reconfiguration - 5 minutes between each

            melting_time = total_packing_time

            full_melting_time = boiling_conf.meltings.serving_time + melting_time + boiling_conf.meltings.salting_time

        # todo: make proper order
        form_factor_label = ' / '.join([str(sku.form_factor) for sku in boiling_request.keys()])
        brand_label = ' / '.join([sku.brand_name for sku in boiling_request.keys()])

        with make('melting', y=10, time_size=full_melting_time, melting_line=melting_line):
            with make(y=0):
                make('melting_label', time_size=4 * 5)
                make('melting_name', time_size=full_melting_time - 4 * 5, form_factor_label=form_factor_label)
            with make(y=1):
                make('serving', time_size=boiling_conf.meltings.serving_time)
                make('melting_process', time_size=melting_time, speed=boiling_conf.meltings.speed)

            with make(y=2):
                make(time_size=boiling_conf.meltings.serving_time, visible=False)
                if boiling_type == 'water':
                    make('cooling1', time_size=boiling_conf.meltings.first_cooling_time)
                    make('cooling2', time_size=boiling_conf.meltings.second_cooling_time)
                elif boiling_type == 'salt':
                    make('salting', time_size=boiling_conf.meltings.salting_time)

        # prepare time
        if boiling_type == 'water':
            prepare_time = boiling_conf.meltings.serving_time + boiling_conf.meltings.first_cooling_time + boiling_conf.meltings.second_cooling_time
        elif boiling_type == 'salt':
            prepare_time = boiling_conf.meltings.serving_time + boiling_conf.meltings.salting_time

        with make('packing', t=prepare_time / 5, time_size=total_packing_time, push_func=add_push):
            with make(y=0):
                make('packing_label', time_size=3 * 5)
                make('packing_name', time_size=total_packing_time - 3 * 5, form_factor_label=form_factor_label)
            with make(y=1):
                make('packing_brand', time_size=total_packing_time, brand_label=brand_label)
            with make(y=2):
                make('configuration', time_size=packing_times[0], visible=False)

                for packing_time in packing_times[1:]:
                    make('configuration', size=1)
                    make('configuration', time_size=packing_time, visible=False)

    res = maker.root.children[0]
    res.rel_props['size'] = max(c.end for c in res.children)

    return res


def make_boiling(boiling_conf, boiling_request, boiling_type='water', block_num=12, pouring_line=None,
                 melting_line=None):
    termizator = db.session.query(Termizator).first()
    termizator.pouring_time = 30

    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    boiling_label = '{} {} {} 8000кг'.format(boiling_conf.percent, boiling_conf.ferment,
                                             'с лактозой' if boiling_conf.is_lactose else 'безлактозная')

    with make('boiling', block_num=block_num, boiling_type=boiling_type, boiling_label=boiling_label):
        # todo: make boiling size

        timings = []
        timings.append(boiling_conf.pourings.pouring_time)
        timings.append(boiling_conf.pourings.soldification_time)
        timings.append(boiling_conf.pourings.cutting_time)
        timings.append(boiling_conf.pourings.pouring_off_time)
        timings.append(boiling_conf.pourings.extra_time)

        with make('pouring', time_size=sum(timings), pouring_line=pouring_line):
            with make(y=0):
                make('termizator', time_size=termizator.pouring_time)
                make('pouring_name', time_size=sum(timings) - termizator.pouring_time)
            with make(y=1):
                make('pouring_and_fermenting', time_size=timings[0])
                make('soldification', time_size=timings[1])
                make('cutting', time_size=timings[2])
                make('pouring_off', time_size=timings[3])
                make('extra', time_size=timings[4])

        # todo: specify parameter
        make('drenator', size=cast_t('03:50'), visible=False)

        make(make_melting_and_packing(boiling_conf, boiling_request, boiling_type, melting_line=melting_line))

    res = maker.root.children[0]
    res.rel_props['size'] = max(c.end for c in res.children)

    return res



def make_termizator_cleaning_block(cleaning_type):
    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    with make('cleaning'):
        if cleaning_type == 'short':
            make('short_cleaning', t=0, size=8)
        elif cleaning_type == 'full':
            make('full_cleaning', t=0, size=16)

    res = maker.root.children[0]
    res.rel_props['size'] = max(c.end for c in res.children)
    return res