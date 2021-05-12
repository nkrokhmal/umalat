from utils_ak.block_tree import *
from app.enum import LineName


def make_cooling_process(
    line_name, cooling_technology, melting_process_size=None, size=None, *args, **kwargs
):
    maker, make = init_block_maker("cooling_process", *args, **kwargs)
    with make("start"):
        cooling_times = (
            [
                cooling_technology.first_cooling_time,
                cooling_technology.second_cooling_time,
            ]
            if line_name == LineName.WATER
            else [cooling_technology.salting_time]
        )
        for cooling_time in cooling_times:
            make("cooling", size=(cooling_time // 5, 0))

    if size:
        melting_process_size = size - maker.root["start"].size[0]

    with make("finish"):
        make("cooling", size=(melting_process_size, 0))
    return maker.root
