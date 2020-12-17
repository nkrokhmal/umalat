from app.schedule_maker.models import *
from app.schedule_maker.utils import *
from app.schedule_maker.utils.time import cast_t, cast_time


def make_melting_and_packing(line_df, boiling_model, boiling_contents):
    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    # [packing.reconfiguration_times]
    def get_configuration_times(skus):
        res = []
        for i in range(len(skus) - 1):
            old_sku, sku = skus[i: i + 2]
            if old_sku is None:
                # todo: display first configuration?
                res.append(0)
            elif boiling_model.boiling_type == 'salt' and old_sku.weight_form_factor != sku.weight_form_factor and cast_packer(old_sku) == cast_packer(sku):
                # todo: take from parameters
                res.append(25)
            elif old_sku == sku:
                res.append(0)
            else:
                # todo: take from parameters
                res.append(5)
        return res

    # [melting.params, packing.params]
    with make('melting_and_packing'):
        # packing and melting time
        packing_times = []
        configuration_times = get_configuration_times([line_df.at[boiling_model.boiling_type, 'last_packing_sku']] + [sku for sku, sku_kg in boiling_contents]) # add last_packing for first configuration

        if boiling_model.boiling_type == 'water':
            # [cheesemakers.boiling_output]
            cheese_from_boiling = 1000  # todo: take from parameters

            # [cheesemakers.boiling_volume]
            cheese_from_boiling *= 8000 / 8000 # todo: make boiling_volume count

            melting_time = custom_round(cheese_from_boiling / boiling_model.meltings.speed * 60, 5, rounding='ceil')

            for sku, sku_kg in boiling_contents:
                packing_speed = min(sku.packing_speed, boiling_model.meltings.speed)
                packing_times.append(custom_round(sku_kg / packing_speed * 60, 5, rounding='ceil'))
            total_packing_time = sum(packing_times) + sum(configuration_times[1:])  # add time for configuration - first is made before packing process
            full_melting_time = boiling_model.meltings.serving_time + melting_time

        elif boiling_model.boiling_type == 'salt':
            for sku, sku_kg in boiling_contents:
                packing_times.append(custom_round(sku_kg / sku.packing_speed * 60, 5, rounding='ceil'))

            total_packing_time = sum(packing_times) + sum(configuration_times[1:])  # add time for configuration - first is made before packing process

            # fit melting time for packing [melting.slow_packing]
            # melting_time = total_packing_time
            melting_time = 50

            full_melting_time = boiling_model.meltings.serving_time + melting_time + boiling_model.meltings.salting_time

        def gen_label(label_weights):
            cur_label = None
            values = []
            for label, weight in label_weights:
                s = ''
                if label != cur_label:
                    s += label + ' '
                    cur_label = label

                # todo: make properly, this if-else if because of rubber. Should be something better
                if weight:
                    s += str(weight / 1000)
                else:
                    s += 'терка'
                values.append(s)
            return '/'.join(values)

        form_factor_label = gen_label([(sku.form_factor.name, sku.weight_form_factor) for sku, sku_kg in boiling_contents])
        brand_label = gen_label([(sku.brand_name, sku.weight_form_factor) for sku, sku_kg in boiling_contents])

        with make('melting', time_size=full_melting_time):
            if boiling_model.boiling_type == 'water':
                with make(orient='vertical', h=1):
                    make('serving', time_size=boiling_model.meltings.serving_time)
            with make(orient='vertical', h=1):
                make('serving', time_size=boiling_model.meltings.serving_time, visible=False)
                make('melting_label', time_size=4 * 5)
                make('melting_name', time_size=full_melting_time - 4 * 5 - boiling_model.meltings.serving_time, form_factor_label=form_factor_label)
            with make(orient='vertical', h=1):
                serving_visible = boiling_model.boiling_type == 'salt'
                make('serving', time_size=boiling_model.meltings.serving_time, visible=serving_visible)
                make('melting_process', time_size=melting_time, speed=boiling_model.meltings.speed)

                if boiling_model.boiling_type == 'salt':
                    make('salting', time_size=boiling_model.meltings.salting_time)
            with make(orient='vertical', h=1):
                make(time_size=boiling_model.meltings.serving_time, visible=False)
                if boiling_model.boiling_type == 'water':
                    make('cooling1', time_size=boiling_model.meltings.first_cooling_time)
                    make('cooling2', time_size=boiling_model.meltings.second_cooling_time)
                elif boiling_model.boiling_type == 'salt':
                    make('salting', time_size=boiling_model.meltings.salting_time)

        # prepare time
        if boiling_model.boiling_type == 'water':
            prepare_time = boiling_model.meltings.serving_time + boiling_model.meltings.first_cooling_time + boiling_model.meltings.second_cooling_time
        elif boiling_model.boiling_type == 'salt':
            prepare_time = boiling_model.meltings.serving_time + boiling_model.meltings.salting_time

        with make('packing_and_preconfiguration', t=(prepare_time - configuration_times[0]) / 5, time_size=total_packing_time + configuration_times[0], push_func=add_push):
            if configuration_times[0]:
                make('configuration', time_size=configuration_times[0], y=2)

            with make('packing', time_size=total_packing_time):
                with make(y=0):
                    make('packing_label', time_size=3 * 5)
                    # use different labels for water and salt
                    if boiling_model.boiling_type == 'water':
                        make('packing_name', time_size=total_packing_time - 3 * 5, form_factor_label=form_factor_label)
                    elif boiling_model.boiling_type == 'salt':
                        make('packing_name', time_size=total_packing_time - 3 * 5, form_factor_label=brand_label)
                with make(y=1):
                    # use different labels for water and salt
                    if boiling_model.boiling_type == 'water':
                        make('packing_brand', time_size=total_packing_time, brand_label=brand_label)
                    elif boiling_model.boiling_type == 'salt':
                        make('packing_brand', time_size=total_packing_time, brand_label='фасовка')
                with make(y=2):
                    make('configuration', time_size=packing_times[0], visible=False)

                    for i, packing_time in enumerate(packing_times[1:]):
                        make('configuration', time_size=configuration_times[i + 1])
                        make('configuration', time_size=packing_time, visible=False)

    res = maker.root.children[0]
    res.props.update({'size': max(c.end for c in res.children)})
    return res


def make_boiling(line_df, boiling_model, boiling_contents, block_num=12, pouring_line=None):
    termizator = db.session.query(Termizator).first()

    # [termizator.time]
    termizator.pouring_time = 30

    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    # [cheesemakers.boiling_volume]
    boiling_volume = 8000  # kg # todo: add different volumes

    # [cheesemakers.boiling_params]
    boiling_label = '{} {} {} {}кг'.format(boiling_model.percent, boiling_model.ferment, '' if boiling_model.is_lactose else 'безлактозная', boiling_volume)

    with make('boiling', block_num=block_num, boiling_type=boiling_model.boiling_type, boiling_label=boiling_label, boiling_id=boiling_model.id):
        # [cheesemakers.boiling_times]
        timings = []
        timings.append(boiling_model.pourings.pouring_time)
        timings.append(boiling_model.pourings.soldification_time)
        timings.append(boiling_model.pourings.cutting_time)
        timings.append(boiling_model.pourings.pouring_off_time)
        timings.append(boiling_model.pourings.extra_time)

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

        make('drenator', time_size=cast_t(line_df.at[boiling_model.boiling_type, 'chedderization_time']) * 5 - timings[3] - timings[4], visible=False)
        make(make_melting_and_packing(line_df, boiling_model, boiling_contents))

    res = maker.root.children[0]
    res.props.update({'size': max(c.end for c in res.children)})

    return res


def make_termizator_cleaning_block(cleaning_type):
    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    # [termizator.cleaning_time]
    cleaning_time = 8 if cleaning_type == 'short' else 16

    with make('cleaning'):
        make(f'{cleaning_type}_cleaning', t=0, size=cleaning_time)

    res = maker.root.children[0]
    res.props.update({'size': max(c.end for c in res.children)})
    return res


def make_template():
    maker = BlockMaker(default_push_func=add_push)
    make = maker.make

    with make('template', beg_time='00:00', index_width=0):
        make(y=2, t=2, h=1, size=1, text='График наливов')
        make(y=6, t=1, h=2, size=3, text='Сыроизготовитель №1 Poly 1', color=(183, 222, 232))
        make(y=9, t=1, h=2, size=3, text='Сыроизготовитель №2 Poly 2', color=(183, 222, 232))
        make(y=12, t=1, h=2, size=3, text='Мойка термизатора')
        make(y=15, t=1, h=2, size=3, text='Сыроизготовитель №3 Poly 3', color=(252, 213, 180))
        make(y=18, t=1, h=2, size=3, text='Сыроизготовитель №4 Poly 4', color=(252, 213, 180))
        make(y=21, t=2, h=1, size=1, text='График цеха плавления')
        make(y=23, t=5, h=1, size=cast_t('19:05') - cast_t('07:00'), text='Оператор + Помощник', color=(149, 179, 215))
        make(y=24, t=1, h=2, size=3, text='Линия плавления моцареллы в воде №1')
        make(y=28, t=5, h=1, size=cast_t('19:05') - cast_t('07:00'), text='бригадир упаковки + 5 рабочих', color=(149, 179, 215))
        make(y=29, t=1, h=2, size=3, text='Фасовка')
        make(y=32, t=5, h=1, size=cast_t('19:00') - cast_t('07:00'), text='1 смена оператор + помощник', color='yellow')
        make(y=32, t=5 + cast_t('19:00') - cast_t('07:00'), h=1, size=cast_t('23:55') - cast_t('19:00') + 1 + cast_t('05:30'), text='1 оператор + помощник', color='red')
        make(y=33, t=1, h=6, size=3, text='Линия плавления моцареллы в рассоле №2')
        make(y=45, t=5, h=1, size=cast_t('19:05') - cast_t('07:00'), text='Бригадир упаковки +5 рабочих упаковки + наладчик', color=(149, 179, 215))
        make(y=45, t=5 + cast_t('19:05') - cast_t('07:00'), h=1, size=cast_t('23:55') - cast_t('19:00') + 1 + cast_t('05:30'), text='бригадир + наладчик + 5 рабочих', color=(240, 184, 183))
        make(y=46, t=1, h=2, size=3, text='Фасовка')

        make(y=4, t=10, h=1, size=cast_t('13:35') - cast_t('01:30'), text='1 смена', color=(141, 180, 226))
        make(y=4, t=4 + cast_t('13:35') - cast_t('01:00'), h=1, size=cast_t('23:55') - cast_t('13:35'), text='2 смена', color=(0, 176, 240))

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
                make(y=21, t=4 + i, size=1, h=1, text=str(int(cur_time[:2])), color=(218, 150, 148), text_rotation=90)
            else:
                make(y=21, t=4 + i, size=1, h=1, text=cur_time[-2:], color=(204, 255, 255), text_rotation=90)

    res = maker.root.children[0]
    res.props.update({'size': max(c.end for c in res.children)})
    return res

if __name__ == '__main__':
    make_template()