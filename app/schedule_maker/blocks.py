from app.schedule_maker.models import *
from app.schedule_maker.utils import *
from app.schedule_maker.utils.time import cast_t, cast_time

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
            total_packing_time = sum(packing_times) + (len(packing_times) - 1) * 5  # add time for reconfiguration - 5 minutes between each
            full_melting_time = boiling_conf.meltings.serving_time + melting_time

        elif boiling_type == 'salt':
            # todo: make proper order
            for sku, sku_kg in boiling_request.items():
                packing_times.append(custom_round(sku_kg / sku.packing_speed * 60, 5, rounding='ceil'))
            total_packing_time = sum(packing_times) + (len(packing_times) - 1) * 5  # add time for reconfiguration - 5 minutes between each

            # fit melting time for packing
            melting_time = total_packing_time

            full_melting_time = boiling_conf.meltings.serving_time + melting_time + boiling_conf.meltings.salting_time

        def gen_label(label_weights):
            cur_label = None
            values = []
            for label, weight in label_weights:
                s = ''
                if label != cur_label:
                    s += label + ' '
                    cur_label = label
                s += str(weight / 1000)
                values.append(s)
            return '/'.join(values)

        form_factor_label = gen_label([(sku.form_factor, sku.weight_netto) for sku in boiling_request.keys()])
        brand_label = gen_label([(sku.brand_name, sku.weight_netto) for sku in boiling_request.keys()])

        with make('melting', y=10, time_size=full_melting_time, melting_line=melting_line):
            # todo: make properly
            cur_y = 0
            if boiling_type == 'water':
                with make(y=cur_y):
                    make('serving', time_size=boiling_conf.meltings.serving_time)
                    cur_y += 1
            with make(y=cur_y):
                make('serving', time_size=boiling_conf.meltings.serving_time, visible=False)
                make('melting_label', time_size=4 * 5)
                make('melting_name', time_size=full_melting_time - 4 * 5 - boiling_conf.meltings.serving_time, form_factor_label=form_factor_label)
                cur_y += 1
            with make(y=cur_y):
                make('serving', time_size=boiling_conf.meltings.serving_time, visible=False)
                make('melting_process', time_size=melting_time, speed=boiling_conf.meltings.speed)

                if boiling_type == 'salt':
                    make('salting', time_size=boiling_conf.meltings.salting_time)
                cur_y += 1
            with make(y=cur_y):
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
                # use different labels for water and salt
                if boiling_type == 'water':
                    make('packing_name', time_size=total_packing_time - 3 * 5, form_factor_label=form_factor_label)
                elif boiling_type == 'salt':
                    make('packing_name', time_size=total_packing_time - 3 * 5, form_factor_label=brand_label)
            with make(y=1):
                # use different labels for water and salt
                if boiling_type == 'water':
                    make('packing_brand', time_size=total_packing_time, brand_label=brand_label)
                elif boiling_type == 'salt':
                    make('packing_brand', time_size=total_packing_time, brand_label='фасовка/confezionamento')
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

    with make('boiling', block_num=block_num, boiling_type=boiling_type, boiling_label=boiling_label, boiling_id=boiling_conf.id):
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



def make_template():
    maker = BlockMaker(default_push_func=add_push)
    make = maker.make

    with make('template', beg_time='00:00', index_width=0):
        make(y=6, t=1, h=2, size=3, text='Сыроизготовитель №1 Poly 1', color=(183, 222, 232))
        make(y=9, t=1, h=2, size=3, text='Сыроизготовитель №2 Poly 2', color=(183, 222, 232))
        make(y=15, t=1, h=2, size=3, text='Сыроизготовитель №3 Poly 3', color=(252, 213, 180))
        make(y=18, t=1, h=2, size=3, text='Сыроизготовитель №4 Poly 4', color=(252, 213, 180))
        make(y=12, t=1, h=2, size=3, text='Мойка термизатора')
        make(y=24, t=1, h=2, size=3, text='Линия плавления моцареллы в воде №1')
        make(y=29, t=1, h=2, size=3, text='Фасовка')
        make(y=33, t=1, h=6, size=3, text='Линия плавления моцареллы в рассоле №2')
        make(y=46, t=1, h=2, size=3, text='Фасовка')

        make(y=4, t=10, h=1, size=cast_t('13:35') - cast_t('01:30'), text='1 смена', color=(141, 180, 226))
        make(y=4, t=4 + cast_t('13:35') - cast_t('01:00'), h=1, size=cast_t('23:55') - cast_t('13:35'),
             text='2 смена', color=(0, 176, 240))

        for i in range(288):
            cur_time = cast_time(i + cast_t('01:00'))
            if cur_time[-2:] == '00':
                make(y=2, t=4 + i, size=1, h=1, text=str(int(cur_time[:2])), color=(218, 150, 148),
                     text_rotation=90)
            else:
                make(y=2, t=4 + i, size=1, h=1, text=cur_time[-2:], color=(204, 255, 255), text_rotation=90)

        for i in range(288):
            cur_time = cast_time(i + cast_t('07:00'))
            if cur_time[-2:] == '00':
                make(y=21, t=4 + i, size=1, h=1, text=str(int(cur_time[:2])), color=(218, 150, 148),
                     text_rotation=90)
            else:
                make(y=21, t=4 + i, size=1, h=1, text=cur_time[-2:], color=(204, 255, 255),
                     text_rotation=90)

    res = maker.root.children[0]
    res.rel_props['size'] = max(c.end for c in res.children)
    return res