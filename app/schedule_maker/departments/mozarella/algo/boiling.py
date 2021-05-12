from app.schedule_maker.departments.mozarella.boiling_plan import *


def make_boiling(boiling_model, boiling_id, boiling_volume, melting_and_packing):
    maker, make = init_block_maker("root")

    bt = boiling_model.boiling_technologies[0]
    with make(
        "boiling",
        boiling_id=boiling_id,
        boiling_volume=boiling_volume,
        boiling_model=boiling_model,
    ):
        with make("pouring"):
            with make("first"):
                make("termizator", size=(boiling_model.line.pouring_time // 5, 0))
                # todo: use boiling technology from outside???

                make(
                    "fermenting",
                    size=(
                        bt.pouring_time // 5 - boiling_model.line.pouring_time // 5,
                        0,
                    ),
                )
                make(
                    "soldification",
                    size=(bt.soldification_time // 5, 0),
                )
                make(
                    "cutting",
                    size=(bt.cutting_time // 5, 0),
                )
                make(
                    "pumping_out",
                    size=(bt.pumping_out_time // 5, 0),
                )
            with make("second"):
                make(
                    "pouring_off",
                    size=(bt.pouring_off_time // 5, 0),
                )
                make("extra", size=(bt.extra_time // 5, 0))
        make(
            "drenator",
            x=(maker.root["boiling"]["pouring"]["first"].y[0], 0),
            size=(boiling_model.line.chedderization_time // 5, 0),
            push_func=add_push,
        )
    push(maker.root["boiling"], melting_and_packing)

    # todo: make proper drenator
    # push(maker.root['boiling'], maker.create_block('full_drenator', x=[maker.root['boiling']['pouring']['second']['pouring_off'].x[0], 0], size=[maker.root['drenator'].size[0] + melting_and_packing['melting']['serving'].size[0] + melting_and_packing['melting']['meltings'].size[0], 0]), push_func=add_push)
    return maker.root["boiling"]
