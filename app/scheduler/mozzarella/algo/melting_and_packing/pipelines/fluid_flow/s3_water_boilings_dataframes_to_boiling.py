from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push

from app.scheduler.mozzarella.algo.boiling import make_boiling
from app.scheduler.mozzarella.algo.cooling import make_cooling_process


class BoilingsDataframesToBoilings:
    def _make_line(self, df, line_name, item_name):
        if len(df) == 0:
            raise Exception("Should not happen")
        start_from = df.iloc[0]["beg"]

        m = BlockMaker(line_name, x=(start_from // 5, 0))

        for i, row in df.iterrows():
            m.row(
                row["name"],
                push_func=add_push,
                size=(row["end"] - row["beg"]) // 5,
                x=row["beg"] // 5 - start_from // 5,
                **{item_name: row["item"]}
            )
        return m.root

    def _make_cooling_line(self, df, boiling_model):
        assert len(df) > 0, "Should not happen"

        start_from = df.iloc[0]["beg"]
        m = BlockMaker("coolings", x=(start_from // 5, 0))

        for i, row in df.iterrows():
            cooling_process = make_cooling_process(
                boiling_model.line.name,
                cooling_technology=row["item"].default_cooling_technology,
                bff=row["item"],
                size=(row["end"] - row["beg"]) // 5,
                x=(row["beg"] // 5 - start_from // 5, 0),
            )
            m.block(cooling_process, push_func=add_push, bff=row["item"])
        return m.root

    def _make_melting_and_packing(self, boiling_dataframes, boiling_model):
        m = BlockMaker("melting_and_packing")

        with m.block("melting"):
            serving = m.row("serving", push_func=add_push, size=boiling_model.line.serving_time // 5).block

            line = self._make_line(boiling_dataframes["meltings"], "meltings", "bff")
            line.props.update(x=(serving.size[0], 0))
            push(m.root["melting"], line, push_func=add_push)

            line = self._make_cooling_line(boiling_dataframes["coolings"], boiling_model)
            line.props.update(x=(serving.size[0], 0))
            push(m.root["melting"], line, push_func=add_push)

        # NOTE: collecting processes are the same with packing processes on water before rounding, but may differ after rounding
        for packing_team_id, df in boiling_dataframes["collectings"].items():
            line = self._make_line(df, "collecting", "sku")
            line.props.update(x=(serving.size[0] + line.x[0], 0), packing_team_id=int(packing_team_id))
            push(m.root, line, push_func=add_push)

        for packing_team_id, df in boiling_dataframes["packings"].items():
            line = self._make_line(df, "packing", "sku")
            line.props.update(x=(serving.size[0] + line.x[0], 0), packing_team_id=int(packing_team_id))
            push(m.root, line, push_func=add_push)
        return m.root

    def __call__(self, boiling_volumes, boilings_dataframes, boiling_model, first_boiling_id):
        res = []
        for i in range(len(boiling_volumes)):
            mp = self._make_melting_and_packing(boilings_dataframes[i], boiling_model)
            boiling = make_boiling(boiling_model, first_boiling_id + i, boiling_volumes[i], mp)
            res.append(boiling)
        return res
