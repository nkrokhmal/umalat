from datetime import datetime

from utils_ak.block_tree import BlockMaker, add_push

from app.scheduler.brynza.make_schedule2.make_schedule2 import make_schedule2
from app.scheduler.common.wrap_header import wrap_header


def wrap_frontend2(
    brynza_boilings: int,
    halumi_boilings: int,
    n_cheese_makers: int = 4,
    date=None,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"brynza": 1},
) -> dict:

    # - Get schedule

    output = make_schedule2(
        brynza_boilings=brynza_boilings,
        halumi_boilings=halumi_boilings,
        n_cheese_makers=n_cheese_makers,
        start_time=start_time,
        first_batch_ids_by_type=first_batch_ids_by_type,
    )
    schedule = output["schedule"]

    # - Plot boilings

    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )
    m.push("stub", size=(0, 1))

    m.push(wrap_header(date=date, start_time=start_time, header="График наливов"))

    # - Make cheese makers

    for cheese_maker_num in range(1, n_cheese_makers + 1):
        with m.push(f"cheese_maker", start_time=start_time):
            for boiling in schedule.iter(
                cls="boiling",
                cheese_maker_num=cheese_maker_num,
            ):
                with m.push(
                    "boiling",
                    boiling_label="label",
                    boiling_id=boiling.props["boiling_id"],
                    x=(boiling.x[0], 0),
                    push_func=add_push,
                    axis=1,
                ):
                    with m.push():
                        m.push_row("boiling_id_label", size=6, boiling_id=boiling.props["boiling_id"])
                        m.push_row(
                            "boiling_name_label",
                            size=boiling.size[0] - 6,
                            boiling_label=f"{boiling.props['group_name'] if boiling.props['group_name'] != 'Чанах' else 'Халуми'} 3,05 PCS(12-13)  3150кг",
                        )
                    with m.push(font_size=8):
                        m.push_row("pouring", size=boiling["pouring"].size[0])
                        m.push_row("soldification", size=boiling["soldification"].size[0])
                        m.push_row("cutting", size=boiling["cutting"].size[0])
                        m.push_row("pouring_off", size=boiling["pouring_off"].size[0])
                        m.push_row("extra", size=2)

        m.push("stub", size=(0, 2))

    # - Make saltings

    # -- Time

    m.push(wrap_header(date=date, start_time=start_time, header="График посолки"))

    # -- Total salting block

    saltings = list(schedule.iter(cls="salting"))
    m.push_row(
        "total_salting",
        x=saltings[0].x[0],
        size=saltings[-1].y[0] - saltings[0].x[0],
        start_time=start_time,
    )

    # -- Saltings

    for cheese_maker_num in range(1, n_cheese_makers + 1):
        with m.push(
            f"salting_cheese_maker",
            start_time=start_time,
        ):
            for salting in schedule.iter(
                cls="salting",
                cheese_maker_num=cheese_maker_num,
                group_name="Брынза",
            ):
                with m.push(
                    "salting",
                    boiling_label="label",
                    salting=salting.props["boiling_id"],
                    x=(salting.x[0], 0),
                    push_func=add_push,
                    axis=1,
                ):
                    with m.push():
                        m.push(
                            "salting_id_label",
                            size=(2, 2),
                            boiling_id=salting.props["boiling_id"],
                        )
                        m.push(
                            "salting_name_label",
                            size=(salting.size[0] - 2, 2),
                            boiling_label="boiling_label",
                        )

    # - Add template

    with m.push("template_block", index_width=1, push_func=add_push):
        for cheese_maker_num in range(1, n_cheese_makers + 1):
            m.push(
                "template",
                push_func=add_push,
                x=(1, 2 + n_cheese_makers * (cheese_maker_num - 1)),
                size=(2, 2),
                text=f"Сыроизготовитель №1 Poly {cheese_maker_num}",
                color=(183, 222, 232),
            )
        m.push(
            "template",
            push_func=add_push,
            x=(1, 5 * n_cheese_makers + 2),
            size=(2, 2),
            text="ПОСОЛКА",
        )

    # - Add frontend to output and return

    output["frontend"] = m.root

    return output


def test():
    print(wrap_frontend2(brynza_boilings=3, halumi_boilings=3)["schedule"])
    print(wrap_frontend2(brynza_boilings=3, halumi_boilings=3)["frontend"])


if __name__ == "__main__":
    test()
