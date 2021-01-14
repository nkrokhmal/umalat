from utils_ak.block_tree import *
from app.enum import LineName


def make_cooling_process(boiling_model, cooling_technology, melting_process_size=None, size=None, *args, **kwargs):
    maker, make = init_block_maker('cooling_process', *args, **kwargs)
    with make('start'):
        if boiling_model.line.name == LineName.water:
            make('cooling', size=(cooling_technology.first_cooling_time // 5, 0))
            make('cooling', size=(cooling_technology.second_cooling_time // 5, 0))
        elif boiling_model.line.name == LineName.salt:
            make('salting', size=(cooling_technology.salting_time // 5, 0))

    if size:
        melting_process_size = size - maker.root['start'].size[0]

    with make('finish'):
        if boiling_model.line.name == LineName.water:
            make('cooling', size=(melting_process_size, 0))
        elif boiling_model.line.name == LineName.salt:
            make('salting', size=(melting_process_size, 0))
    return maker.root