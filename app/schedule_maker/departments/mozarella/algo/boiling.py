from app.schedule_maker.departments.mozarella.boiling_plan import *


def make_boiling(boiling_model, boiling_id, boiling_volume, melting_and_packing):
    maker, make = init_block_maker("root")

    with make(
        "boiling",
        boiling_id=boiling_id,
        boiling_volume=boiling_volume,
        boiling_model=boiling_model,
    ):
        with make("pouring"):
            with make("first"):
                make("termizator", size=(boiling_model.line.pouring_time // 5, 0))
                make(
                    "fermenting",
                    size=(
                        boiling_model.boiling_technology.pouring_time // 5
                        - boiling_model.line.pouring_time // 5,
                        0,
                    ),
                )
                make(
                    "soldification",
                    size=(boiling_model.boiling_technology.soldification_time // 5, 0),
                )
                make(
                    "cutting",
                    size=(boiling_model.boiling_technology.cutting_time // 5, 0),
                )
                make(
                    "pumping_out",
                    size=(boiling_model.boiling_technology.pumping_out_time // 5, 0),
                )
            with make("second"):
                make(
                    "pouring_off",
                    size=(boiling_model.boiling_technology.pouring_off_time // 5, 0),
                )
                make(
                    "extra", size=(boiling_model.boiling_technology.extra_time // 5, 0)
                )
        make(
            "drenator",
            x=(maker.root["boiling"]["pouring"]["first"].y[0], 0),
            size=(boiling_model.line.chedderization_time // 5, 0),
            push_func=add_push,
        )
        with make("steams"):
            make(
                "steam_consumption",
                x=(0, 0),
                size=(6, 0),
                value=1100,
                push_func=add_push,
            )

            if boiling_model.line.name == LineName.SALT:
                make(
                    "steam_consumption",
                    x=(
                        maker.root["boiling"]["pouring"]["first"]["pumping_out"].x[0]
                        - 3,
                        0,
                    ),
                    size=(3, 0),
                    value=700,
                    push_func=add_push,
                )

    # add steams to melting_and_packing
    value = 250 if boiling_model.line.name == LineName.WATER else 1200
    push(
        melting_and_packing,
        maker.create_block(
            "steam_consumption",
            size=(
                melting_and_packing["melting"]["serving"].size[0]
                + melting_and_packing["melting"]["meltings"].size[0],
                0,
            ),
            value=value,
            type="melting",
        ),
        push_func=add_push,
    )

    push(maker.root["boiling"], melting_and_packing)

    return maker.root["boiling"]
