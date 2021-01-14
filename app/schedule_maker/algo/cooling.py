from utils_ak.block_tree import *
from app.schedule_maker.models import cast_boiling_form_factor
# todo: take parameters from boiling_form_factor

# todo: use bff
def make_cooling_process(boiling_model, melting_process_size=None, size=None, *args, **kwargs):
    maker, make = init_block_maker('cooling_process', *args, **kwargs)
    with make('start'):
        if boiling_model.boiling_type == 'water':
            make('cooling', size=(cooling_times['first_cooling_time'] // 5, 0))
            make('cooling', size=(cooling_times['second_cooling_time'] // 5, 0))
        elif boiling_model.boiling_type == 'salt':
            make('salting', size=(cooling_times['salting_time'] // 5, 0))

    if size:
        melting_process_size = size - maker.root['start'].size[0]

    with make('finish'):
        if boiling_model.boiling_type == 'water':
            make('cooling', size=(melting_process_size, 0))
        elif boiling_model.boiling_type == 'salt':
            make('salting', size=(melting_process_size, 0))
    return maker.root