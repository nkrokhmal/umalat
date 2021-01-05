from app.schedule_maker.dataframes import *


def make_boiling(boiling_model, boiling_id, melting_and_packing):
    maker, make = init_block_maker('root')

    termizator = db.session.query(Termizator).first()

    with make('boiling', boiling_id=boiling_id, boiling_model=boiling_model):
        with make('pouring'):
            with make('first'):
                make('termizator', size=(termizator.pouring_time // 5, 0))
                make('fermenting', size=(boiling_model.pourings.pouring_time // 5 - termizator.pouring_time // 5, 0))
                make('soldification', size=(boiling_model.pourings.soldification_time // 5, 0))
                make('cutting', size=(boiling_model.pourings.cutting_time // 5, 0))
            with make('second'):
                make('pouring_off', size=(boiling_model.pourings.pouring_off_time // 5, 0))
                make('extra', size=(boiling_model.pourings.extra_time // 5, 0))

        make('drenator',
             x=(maker.root['boiling']['pouring']['first'].y[0], 0),
             size=(boiling_model.lines.cheddarization_time // 5, 0),
             push_func=add_push)

    push(maker.root['boiling'], melting_and_packing)
    return maker.root['boiling']

