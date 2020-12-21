from app.schedule_maker.models import *
from app.schedule_maker.utils import *
from app.schedule_maker.utils.time import cast_t, cast_time


def make_melting_and_packing(line_df, boiling_model, boiling_grp, boiling_plan_df):
    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    # mark groups
    cur_group = 0
    cur_form_factor = None
    group_values = []
    for i, row in boiling_grp.iterrows():
        if row['bff'] != cur_form_factor:
            cur_group += 1
            cur_form_factor = row['bff']
        group_values.append(cur_group)
    boiling_grp['group'] = group_values

    # generate labels
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

    form_factor_label = gen_label([(sku.form_factor.short_name, sku.weight_form_factor) for sku, sku_kg in boiling_grp[['sku', 'kg']].values.tolist()])
    brand_label = gen_label([(sku.brand_name, sku.weight_form_factor) for sku, sku_kg in boiling_grp[['sku', 'kg']].values.tolist()])

    # [melting.params, packing.params]
    with make('melting_and_packing', form_factor_label=form_factor_label, brand_label=brand_label):
        melting_events = []
        with make('melting'):
            labels = make('labels', h=1, push_func=dummy_push_y).block
            meltings = make('meltings', h=1, push_func=dummy_push_y).block
            coolings = make('coolings', push_func=add_push).block

            # add first serving as time
            dummy_push(meltings, Block('serving', time_size=boiling_model.meltings.serving_time, visible=False))

            full_melting_process = Block('full_melting_process')
            dummy_push(meltings, full_melting_process)

            for group, grp in boiling_grp.groupby('group'):
                if group > 1:
                    # non-first group - reconfigure time
                    dummy_push(full_melting_process, Block('melting_configuration', size=1))

                melting_process = dummy_push(full_melting_process, Block('melting_process', time_size=custom_round(grp['kg'].sum() / boiling_model.meltings.speed * 60, 5, 'ceil')))

                # add cooling
                cooling_process = Block('cooling_process', t=melting_process.beg())
                cooling_maker = BlockMaker(cooling_process, default_push_func=dummy_push)
                cooling_make = cooling_maker.make

                with cooling_make('start'):
                    if boiling_model.boiling_type == 'water':
                        cooling_make('cooling', time_size=boiling_model.meltings.first_cooling_time)
                        cooling_make('cooling', time_size=boiling_model.meltings.second_cooling_time)
                    elif boiling_model.boiling_type == 'salt':
                        cooling_make('salting', time_size=boiling_model.meltings.salting_time)

                with cooling_make('finish'):
                    if boiling_model.boiling_type == 'water':
                        cooling_make('cooling', time_size=melting_process.props['time_size'])
                    elif boiling_model.boiling_type == 'salt':
                        cooling_make('salting', time_size=melting_process.props['time_size'])

                add_push(coolings, cooling_process)

                melting_events.append({'beg': cooling_process['start'].end(),
                                       'time_size': grp['kg'].sum() / boiling_model.meltings.speed * 60,
                                       'speed': boiling_model.meltings.speed,
                                       'kg': grp['kg'].sum(),
                                       'bff': grp.iloc[0]['bff']})

            dummy_push(labels, Block('serving', time_size=boiling_model.meltings.serving_time))
            dummy_push(labels, Block('melting_name', time_size=meltings.length() * 5 - boiling_model.meltings.serving_time - boiling_model.meltings.serving_time))

        # calculate packings
        packing_teams = pack(melting_events, boiling_plan_df)

        # add packings
        with make('packing', t=full_melting_process.beg(), push_func=add_push):
            for team_id, team in packing_teams.items():
                assert is_int_like(team_id)
                if team.packings:
                    # todo: make team_id coordinate properly
                    with make('packing_team', y=int(team_id) - 1, team_id=team_id, push_func=add_push):
                        print(team_id, team.packings)
                        for beg, end, row in team.packings:
                            assert is_int_like(beg) and is_int_like(end)
                            beg, end = int(beg), int(end)
                            with make('packing_block'):
                                with make('packing_header', t=beg, y=0, push_func=add_push):
                                    make('packing_label', size=3)
                                    make('packing_brand', size=end - beg - 3)
                                make('packing_process', y=1, t=beg, size=end - beg, push_func=add_push)
    return maker.root.children[0]


def pack(melting_events, boiling_plan_df):
    # generate packings with event manager
    em = SimpleEventManager()

    # collect incoming speed of cheese
    class Meltings:
        def __init__(self):
            self.df = pd.DataFrame(columns=['speed', 'kg'])
            self.last_ts = None

        def on_melting(self, topic, ts, event):
            if event['bff'] not in self.df.index:
                self.df.at[event['bff'], 'kg'] = 0
            self.df.at[event['bff'], 'speed'] = event['speed']

        def update(self, topic, ts, event):
            if self.last_ts is None:
                self.last_ts = ts
                return

            self.df['kg'] += (ts - self.last_ts) / 3600 * self.df['speed']
            self.last_ts = ts


    meltings = Meltings()

    em.subscribe('', meltings.update)
    em.subscribe('melting', meltings.on_melting)

    for me in melting_events:
        em.add_event('melting', me['beg'] * 300, me)
        me = dict(me)
        me['speed'] = 0
        em.add_event('melting', me['beg'] * 300 + me['time_size'] * 60, me)

    for i in range(288):
        em.add_event('checkpoint', i * 300, {})


    class PackerTeam:
        def __init__(self, meltings, df, team_id):
            self.meltings = meltings
            self.df = df
            self.df['collected'] = 0.

            self.last_ts = None

            self.packing_start_ts = None
            self.packings = []

            self.team_id = team_id

        def update(self, topic, ts, event):
            df = self.df[self.df['packing_left'].abs() > 1e-2]
            df = df[df['packing_team_id'] == self.team_id]

            if len(df) == 0:
                return

            if not self.last_ts:
                self.last_ts = ts
                return

            cur_row = df.iloc[0] # pack one sku at one time
            if cur_row['bff'] in self.meltings.df.index:
                # take as much as we can
                available = self.meltings.df.at[cur_row['bff'], 'kg']
                needed = cur_row['packing_left']
                collected = min([(ts - self.last_ts) / 3600 * cur_row['speed'],
                                 available,
                                 needed])
                self.df.at[cur_row.name, 'packing_left'] -= collected
                self.meltings.df.at[cur_row['bff'], 'kg'] -= collected
                self.df.at[cur_row.name, 'collected'] += collected

                if not self.packing_start_ts and collected:
                    # start packing
                    self.packing_start_ts = self.last_ts

            if abs(self.df.at[cur_row.name, 'packing_left']) < 1e-2:
                # finish packing

                beg = self.packing_start_ts / 300
                end = ts / 300
                self.packings.append([beg, end, self.df.iloc[0]])
                self.packing_start_ts = None

            self.last_ts = ts

            # todo: add packing configuration

    packing_teams = {}
    for team_id in boiling_plan_df['packing_team_id'].unique():
        packing_teams[team_id] = PackerTeam(meltings, boiling_plan_df, team_id=team_id)
        em.subscribe('checkpoint', packing_teams[team_id].update)

    em.run()
    return packing_teams


def make_boiling(line_df, boiling_model, boiling_grp, boiling_plan_df, block_num=12, pouring_line=None):
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
            with make(h=1, push_func=dummy_push_y):
                make('termizator', time_size=termizator.pouring_time)
                make('pouring_name', time_size=sum(timings) - termizator.pouring_time)
            with make(h=1, push_func=dummy_push_y):
                make('pouring_and_fermenting', time_size=timings[0])
                make('soldification', time_size=timings[1])
                make('cutting', time_size=timings[2])
                make('pouring_off', time_size=timings[3])
                make('extra', time_size=timings[4])

        make('drenator', time_size=cast_t(line_df.at[boiling_model.boiling_type, 'chedderization_time']) * 5 - timings[3] - timings[4], visible=False)
        make(make_melting_and_packing(line_df, boiling_model, boiling_grp, boiling_plan_df))

    return maker.root.children[0]


def make_termizator_cleaning_block(cleaning_type):
    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    # [termizator.cleaning_time]
    cleaning_time = 8 if cleaning_type == 'short' else 16

    with make('cleaning'):
        make(f'{cleaning_type}_cleaning', t=0, size=cleaning_time)

    return maker.root.children[0]


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

    return maker.root.children[0]

if __name__ == '__main__':
    make_template()