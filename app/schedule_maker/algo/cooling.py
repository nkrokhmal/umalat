from utils_ak.block_tree import *
from app.enum import LineName


def make_cooling_process(line_name, cooling_technology, melting_process_size=None, size=None, *args, **kwargs):
    maker, make = init_block_maker('cooling_process', *args, **kwargs)
    with make('start'):
        if line_name == LineName.WATER:
            make('cooling', size=(cooling_technology.first_cooling_time // 5, 0))
            make('cooling', size=(cooling_technology.second_cooling_time // 5, 0))
        elif line_name == LineName.SALT:
            make('salting', size=(cooling_technology.salting_time // 5, 0))

    if size:
        melting_process_size = size - maker.root['start'].size[0]

    with make('finish'):
        if line_name == LineName.WATER:
            make('cooling', size=(melting_process_size, 0))
        elif line_name == LineName.SALT:
            make('salting', size=(melting_process_size, 0))
    return maker.root