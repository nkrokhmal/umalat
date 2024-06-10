import pandas as pd

from utils_ak.fluid_flow.actors.container import Container
from utils_ak.fluid_flow.actors.hub import Hub
from utils_ak.fluid_flow.actors.pipe import pipe_connect, pipe_disconnect
from utils_ak.fluid_flow.actors.processor import Processor
from utils_ak.fluid_flow.actors.queue import Queue
from utils_ak.fluid_flow.actors.sequence import Sequence
from utils_ak.fluid_flow.fluid_flow import FluidFlow, run_flow
from utils_ak.numeric.numeric import custom_round

from app.enum import LineName
from app.globals import ERROR


class SchemaToBoilingsDataframes:
    def _calc_melting_actors_by_boiling(self, boilings_meltings, melting_speed):

        # generate meltings by boilings
        res = []
        for boiling_meltings in boilings_meltings:
            boiling_volume = sum(kg for bff, kg in boiling_meltings)

            drenator = Container("Drenator", value=boiling_volume, max_pressures=[None, None])

            melting_processors = []
            cooling_processors = []
            for i, (bff, kg) in enumerate(boiling_meltings):
                melting_processor = Processor(
                    f"Melting{i}",
                    items=["cheese_mass", bff],
                    max_pressures=[melting_speed, melting_speed],
                    processing_time=0,
                    limits=[kg, kg],
                )
                melting_processors.append(melting_processor)

                cooling_processor = Processor(
                    f"Cooling{i}",
                    items=[bff, bff],
                    max_pressures=[None, None],
                    processing_time=bff.default_cooling_technology.time / 60,
                    limits=[kg, kg],
                )
                cooling_processors.append(cooling_processor)
            melting_queue = Queue(
                "MeltingQueue",
                melting_processors,
                break_funcs={"in": lambda old, new: 1 / 12},
            )
            cooling_queue = Queue("CoolingQueue", cooling_processors)

            res.append([drenator, melting_queue, cooling_queue])
        return res

    def _calc_packing_queues(self, packings):

        # generate packing queues
        packing_queues = {}
        for packing_team_id, grp in sorted(packings.items(), key=lambda v: v[0]):
            sequences = []

            for j, (sku, bff, kg) in enumerate(grp):
                if sku.collecting_speed:
                    assert (
                        sku.packing_speed == sku.collecting_speed
                    ), f"SKU {sku.name} имеет разные скорости сборки и фасовки. На линии воды позволяются только одинаковые скорости сборки и фасовки."

                container = Container(
                    f"Container{packing_team_id}-{j}",
                    item=bff,
                    limits=[kg, None],
                    max_pressures=[sku.packing_speed, None],
                )
                processor = Processor(
                    f"Processor{packing_team_id}-{j}",
                    items=[bff, sku],
                    max_pressures=[sku.packing_speed, None],
                    processing_time=0,
                )
                seq = Sequence(f"Sequence{packing_team_id}-{j}", [container, processor])
                sequences.append(seq)
            packing_queue = Queue(
                f"PackingQueue{packing_team_id}",
                sequences,
                break_funcs={"in": lambda old, new: 1 / 12},
            )
            packing_queues[packing_team_id] = packing_queue
        return packing_queues

    def _calc_boilings_dataframes(self, melting_actors_by_boiling, packing_queues, rounding="nearest_half_down"):
        res = []

        for drenator, melting_queue, cooling_queue in melting_actors_by_boiling:
            boiling_dataframes = {}

            packing_hub = Hub("hub")

            pipe_connect(drenator, melting_queue, "drenator-melting")
            pipe_connect(melting_queue, cooling_queue, "melting-cooling")
            pipe_connect(cooling_queue, packing_hub, "cooling-hub")

            for packing_team_id, packing_queue in packing_queues.items():
                pipe_connect(packing_hub, packing_queue, f"hub-packing_queue{packing_team_id}")

            flow = FluidFlow(drenator, verbose=False)
            run_flow(flow)

            df = pd.DataFrame(melting_queue.active_periods("out"), columns=["item", "beg", "end"])
            df["name"] = "melting_process"
            boiling_dataframes["meltings"] = df

            assert (
                abs(drenator.value) < ERROR
            ), f"Дренатор не был опустошен полностью во время плавления на линии {LineName.WATER} из-за невалидного плана варок. Поправьте план варок и повторите попытку. "
            assert all(
                abs(container.io_containers["out"].value) < ERROR for container in cooling_queue.lines
            ), f"Некоторые SKU не были собраны полностью во время паковки на линии {LineName.WATER} из-за невалидного плана варок. Поправьте план варок и повторите попытку. "

            df = pd.DataFrame(cooling_queue.active_periods(), columns=["item", "beg", "end"])
            df["name"] = "cooling_process"
            boiling_dataframes["coolings"] = df

            boiling_dataframes["collectings"] = {}
            boiling_dataframes["packings"] = {}
            for packing_team_id, queue in packing_queues.items():
                df1 = pd.DataFrame(queue.active_periods("out"), columns=["item", "beg", "end"])
                df1["name"] = "process"

                df2 = pd.DataFrame(queue.breaks, columns=["beg", "end"])
                df2["name"] = "packing_configuration"
                df2["item"] = None
                df = pd.concat([df1, df2]).sort_values(by="beg").reset_index(drop=True)

                # remove last packing configuration if needed
                if df.iloc[-1]["name"] == "packing_configuration":
                    df = df.iloc[:-1]

                boiling_dataframes["packings"][packing_team_id] = df
                boiling_dataframes["collectings"][packing_team_id] = df.copy()

            boiling_dataframes["meltings"] = self._post_process_dataframe(
                boiling_dataframes["meltings"], rounding=rounding
            )
            boiling_dataframes["coolings"] = self._post_process_dataframe(
                boiling_dataframes["coolings"],
                fix_small_intervals=False,
                rounding=rounding,
            )

            boiling_dataframes["collectings"] = {
                packing_team_id: self._post_process_dataframe(df, rounding=rounding)
                for packing_team_id, df in boiling_dataframes["collectings"].items()
            }
            boiling_dataframes["packings"] = {
                packing_team_id: self._post_process_dataframe(df, rounding=rounding)
                for packing_team_id, df in boiling_dataframes["packings"].items()
            }

            res.append(boiling_dataframes)

            # clean-up
            for node in drenator.iterate("down"):
                node.reset()

            # remove packers from current boiling
            for packing_queue in packing_queues.values():
                pipe_disconnect(packing_hub, packing_queue)
        return res

    def _post_process_dataframe(self, df, fix_small_intervals=True, rounding="nearest_half_down"):

        # move to minutes
        df["beg"] = df["beg"] * 60
        df["end"] = df["end"] * 60
        if rounding:

            # round to five-minute intervals
            df["beg"] = df["beg"].apply(lambda ts: None if ts is None else custom_round(ts, 5, rounding))
            df["end"] = df["end"].apply(lambda ts: None if ts is None else custom_round(ts, 5, rounding))

            # fix small intervals (like beg and end: 5, 5 -> 5, 10)
            if fix_small_intervals:
                for i in range(len(df)):
                    if i >= 1:
                        while df.at[i, "beg"] < df.at[i - 1, "end"]:
                            df.at[i, "beg"] += 5

                    while df.at[i, "beg"] >= df.at[i, "end"]:
                        df.at[i, "end"] += 5
            df["beg"] = df["beg"].astype(int)
            df["end"] = df["end"].astype(int)
        return df

    def __call__(self, boilings_meltings, packings, melting_speed, rounding="nearest_half_down"):
        melting_actors_by_boiling = self._calc_melting_actors_by_boiling(boilings_meltings, melting_speed)
        packing_queues = self._calc_packing_queues(packings)
        boilings_dataframes = self._calc_boilings_dataframes(
            melting_actors_by_boiling, packing_queues, rounding=rounding
        )
        return boilings_dataframes
