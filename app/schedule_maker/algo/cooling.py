from utils_ak.block_tree import *


def make_cooling_process(boiling_model, melting_process_size, *args, **kwargs):
    maker, make = init_block_maker('cooling_process', *args, **kwargs)
    with make('start'):
        if boiling_model.boiling_type == 'water':
            make('cooling', size=(boiling_model.meltings.first_cooling_time // 5, 0))
            make('cooling', size=(boiling_model.meltings.second_cooling_time // 5, 0))
        elif boiling_model.boiling_type == 'salt':
            make('salting', size=(boiling_model.meltings.salting_time // 5, 0))
    with make('finish'):
        if boiling_model.boiling_type == 'water':
            make('cooling', size=(melting_process_size, 0))
        elif boiling_model.boiling_type == 'salt':
            make('salting', size=(melting_process_size, 0))
    return maker.root