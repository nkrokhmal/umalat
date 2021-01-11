from utils_ak.block_tree import *
from app.schedule_maker.algo.cooling import make_cooling_process
from app.schedule_maker.algo.boiling import make_boiling
from app.schedule_maker.calculation import *

class boilings_dataframes_to_boilings:
    def _make_line(self, df, line_name, process_name, filler_name, item_name, make_fillers=True):
        if len(df) == 0:
            raise Exception('Should not happen')
        start_from = df.iloc[0]['beg']

        maker, make = init_block_maker(line_name, x=(start_from // 5, 0))

        for i in range(len(df)):
            cur_row = df.iloc[i]
            next_row = None if i == len(df) - 1 else df.iloc[i + 1]  # todo: use simple_bounded_iterator?

            # todo: refactor item_name, make general key item in process?
            make(process_name, size=((cur_row['end'] - cur_row['beg']) // 5, 0), x=(cur_row['beg'] // 5 - start_from // 5, 0), push_func=add_push, **{item_name: cur_row['item']})

            if make_fillers and next_row is not None:
                beg = cur_row['end']
                end = next_row['beg']
                if abs(end - beg) > ERROR:
                    make(filler_name, size=((end - beg) // 5, 0), x=(beg // 5 - start_from // 5, 0), push_func=add_push)
        return maker.root

    def _make_cooling_line(self, df, boiling_model):
        if len(df) == 0:
            raise Exception('Should not happen')
        start_from = df.iloc[0]['beg']
        maker, make = init_block_maker('coolings', x=(start_from // 5, 0))

        for i in range(len(df)):
            cur_row = df.iloc[i]
            cooling_process = make_cooling_process(boiling_model, size=(cur_row['end'] - cur_row['beg']) // 5, x=(cur_row['beg'] // 5 - start_from // 5, 0))
            make(cooling_process, push_func=add_push, bff=cur_row['item'])
        return maker.root

    def _make_melting_and_packing(self, boiling_dataframes, boiling_model):
        maker, make = init_block_maker('melting_and_packing')

        with make('melting'):
            serving = make('serving', size=(boiling_model.meltings.serving_time // 5, 0), push_func=add_push).block

            line = self._make_line(boiling_dataframes['meltings'], 'meltings', 'melting_process', 'melting_configuration', 'bff')
            line.props.update({'x': (serving.size[0], 0)})
            push(maker.root['melting'], line, push_func=add_push)

            line = self._make_cooling_line(boiling_dataframes['coolings'], boiling_model)
            line.props.update({'x': (serving.size[0], 0)})
            push(maker.root['melting'], line, push_func=add_push)

        for packing_team_id, df in enumerate(boiling_dataframes['packings'], 1):
            line = self._make_line(df, 'packing', 'packing_process', 'packing_configuration', 'sku')
            line.props.update({'x': (serving.size[0] + line.x[0], 0), 'packing_team_id': int(packing_team_id)})
            push(maker.root, line, push_func=add_push)
        return maker.root

    def __call__(self, boilings_dataframes, boiling_model, start_from_id):
        res = []
        for i, boiling_dataframes in enumerate(boilings_dataframes):
            mp = self._make_melting_and_packing(boiling_dataframes, boiling_model)
            boiling = make_boiling(boiling_model, start_from_id + i, mp)
            res.append(boiling)
        return res
