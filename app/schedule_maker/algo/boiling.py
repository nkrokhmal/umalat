from app.schedule_maker.boiling_plan import *


def make_boiling(boiling_model, boiling_id, melting_and_packing):
    maker, make = init_block_maker('root')

    with make('boiling', boiling_id=boiling_id, boiling_model=boiling_model):
        with make('pouring'):
            with make('first'):
                make('termizator', size=(boiling_model.line.pouring_time // 5, 0))
                make('fermenting', size=(boiling_model.boiling_technology.pouring_time // 5 - boiling_model.line.pouring_time // 5, 0))
                make('soldification', size=(boiling_model.boiling_technology.soldification_time // 5, 0))
                make('cutting', size=(boiling_model.boiling_technology.cutting_time // 5, 0))
            with make('second'):
                make('pouring_off', size=(boiling_model.boiling_technology.pouring_off_time // 5, 0))
                make('extra', size=(boiling_model.boiling_technology.extra_time // 5, 0))

        make('drenator',
             x=(maker.root['boiling']['pouring']['first'].y[0], 0),
             size=(boiling_model.line.chedderization_time // 5, 0),
             push_func=add_push)

    push(maker.root['boiling'], melting_and_packing)
    return maker.root['boiling']

