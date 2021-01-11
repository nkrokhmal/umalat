from utils_ak.fluid_flow import *
from utils_ak.numeric import *


class SchemaToBoilingsDataFramesTransformer:
    def _calc_melting_actors_by_boiling(self, boilings_meltings, melting_speed):
        # generate meltings by boilings
        res = []
        for boiling_meltings in boilings_meltings:
            boiling_volume = sum(x[1] for x in boiling_meltings)

            drenator = Container('Drenator', value=boiling_volume, max_pressures=[None, None])

            melting_processors = []
            cooling_processors = []
            for i, (bff, kg) in enumerate(boiling_meltings):
                melting_processor = Processor(f'Melting{i}',
                                              items=['cheese_mass', bff],
                                              max_pressures=[melting_speed, melting_speed],
                                              processing_time=0,
                                              limits=[kg, kg])
                melting_processors.append(melting_processor)

                cooling_processor = Processor(f'Cooling{i}',
                                              items=[bff, bff],
                                              max_pressures=[None, None],
                                              processing_time=bff.post_processing_time / 60,
                                              limits=[kg, kg])
                cooling_processors.append(cooling_processor)
            melting_queue = Queue('MeltingQueue', melting_processors, break_funcs={'in': lambda old, new: 1 / 12})
            cooling_queue = Queue('CoolingQueue', cooling_processors)

            res.append([drenator, melting_queue, cooling_queue])
        return res

    def _calc_packing_queues(self, packings):
        # generate packing queues
        packing_queues = []
        for packing_team_id, grp in sorted(packings.items(), key=lambda v: v[0]):
            processors = []

            for j, (sku, bff, kg) in enumerate(grp):
                processor = Processor(f'Packing{j}',
                                      items=[bff, sku],
                                      max_pressures=[sku.packing_speed, None],
                                      processing_time=0,
                                      limits=[kg, None])
                processors.append(processor)
            packing_queue = Queue(f'PackingQueue{packing_team_id}', processors, break_funcs={'in': lambda old, new: 1 / 12})
            packing_queues.append(packing_queue)
        return packing_queues

    def _calc_boilings_dataframes(self, melting_actors_by_boiling, packing_queues):
        res = []

        for drenator, melting_queue, cooling_queue in melting_actors_by_boiling:
            boiling_dataframes = {}

            packing_hub = Hub('hub')

            pipe_connect(drenator, melting_queue, 'drenator-melting')
            pipe_connect(melting_queue, cooling_queue, 'melting-cooling')
            pipe_connect(cooling_queue, packing_hub, 'cooling-hub')

            for i, packing_queue in enumerate(packing_queues):
                pipe_connect(packing_hub, packing_queue, f'hub-packing_queue{i}')

            flow = FluidFlow(drenator, verbose=False)
            run_flow(flow)

            # debug
            #         maker, make = init_block_maker('root', axis=1)
            #         for node in drenator.iterate('down'):
            #             if node.active_periods():
            #                 for period in node.active_periods():
            #                     label = '-'.join([str(node.id), str(period[0])])
            #                     beg, end = period[1:]
            #                     beg, end = custom_round(beg * 60, 5, 'ceil') // 5, custom_round(end * 60, 5, 'ceil') // 5
            #                     make(label, x=[beg, 0], size=(end - beg, 1))
            #         print(maker.root.tabular())

            boiling_dataframes['meltings'] = self._post_process_dataframe(pd.DataFrame(melting_queue.active_periods(), columns=['item', 'beg', 'end']))
            boiling_dataframes['coolings'] = self._post_process_dataframe(pd.DataFrame(cooling_queue.active_periods(), columns=['item', 'beg', 'end']))
            # todo: make dictionary
            boiling_dataframes['packings'] = [self._post_process_dataframe(pd.DataFrame(packing_queue.active_periods('out'), columns=['item', 'beg', 'end'])) for packing_queue in packing_queues]

            res.append(boiling_dataframes)

            # clean-up
            for node in drenator.iterate('down'):
                node.reset()

            # remove packers from current boiling
            for packing_queue in packing_queues:
                pipe_disconnect(packing_hub, packing_queue)
        return res

    def _post_process_dataframe(self, df):
        # move to minutes
        df['beg'] = df['beg'] * 60
        df['end'] = df['end'] * 60

        # round last end up?
        #         df.at[df.index[-1], 'end'] = custom_round(df.at[df.index[-1], 'end'], 5, 'ceil')

        # round to five-minute intervals
        df['beg'] = df['beg'].apply(lambda ts: None if ts is None else custom_round(ts, 5))
        df['end'] = df['end'].apply(lambda ts: None if ts is None else custom_round(ts, 5))

        # fix small intervals (like beg_ts and end_ts: 5, 5 -> 5, 10)
        for i in range(len(df)):
            if i >= 1:
                while df.at[i, 'beg'] <= df.at[i - 1, 'end']:
                    df.at[i, 'beg'] += 5

            while df.at[i, 'beg'] >= df.at[i, 'end']:
                df.at[i, 'end'] += 5

        return df

    def __call__(self, boilings_meltings, packings, melting_speed):
        melting_actors_by_boiling = self._calc_melting_actors_by_boiling(boilings_meltings, melting_speed)
        packing_queues = self._calc_packing_queues(packings)
        boilings_dataframes = self._calc_boilings_dataframes(melting_actors_by_boiling, packing_queues)
        return boilings_dataframes