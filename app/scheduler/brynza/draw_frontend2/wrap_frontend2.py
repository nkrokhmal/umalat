from datetime import datetime

from utils_ak.block_tree import BlockMaker, add_push

from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.brynza.make_schedule2.make_schedule2 import make_schedule2
from app.scheduler.brynza.make_schedule.make_schedule import make_packing_schedule
from app.scheduler.wrap_header import wrap_header


def wrap_frontend2(
    brynza_kg: int,
    chanah_kg: int,
    date=None,
    start_time: str = "07:00",
) -> dict:
    # - Get schedule

    output = make_schedule2(
        brynza_kg=brynza_kg,
        chanah_kg=chanah_kg,
        start_time=start_time,
    )
    schedule = output["schedule"]

    # - Plot boilings

    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.block("stub", size=(0, 1))

    # m.block(wrap_header(date=date, start_time=start_time, header="График наливов"))

    # - Make cheese makers

    for cheese_maker_num in range(1, 5):
        with m.block(f"cheese_maker"):
            for boiling in schedule.iter(
                cls="boiling",
                cheese_maker_num=cheese_maker_num,
            ):
                with m.block(
                    "boiling",
                    boiling_label="label",
                    boiling_id=boiling.props["boiling_id"],
                    x=(boiling.x[0], 0),
                    push_func=add_push,
                    axis=1,
                ):
                    with m.block():
                        m.row("boiling_id_label", size=6, boiling_id=boiling.props["boiling_id"])
                        m.row(
                            "boiling_name_label",
                            size=boiling.size[0] - 6,
                            boiling_label=f"{'Брынза' if boiling.props['group_name'] == 'Брынза' else 'Халуми'} 3,05 PCS(12-13)  3150кг",
                        )
                    with m.block(font_size=8):
                        m.row("pouring", size=boiling["pouring"].size[0])
                        m.row("soldification", size=boiling["soldification"].size[0])
                        m.row("cutting", size=boiling["cutting"].size[0])
                        m.row("pouring_off", size=boiling["pouring_off"].size[0])
                        m.row("extra", size=2)

        m.block("stub", size=(0, 2))

    # - Make saltings

    # -- Total salting block

    saltings = list(schedule.iter(cls="salting"))
    m.row("total_salting", x=saltings[0].x[0], size=saltings[-1].y[0] - saltings[0].x[0])

    # -- Saltings

    for cheese_maker_num in range(1, 5):
        with m.block(f"salting_cheese_maker"):
            for salting in schedule.iter(
                cls="salting",
                cheese_maker_num=cheese_maker_num,
                group_name="Брынза",
            ):
                with m.block(
                    "salting",
                    boiling_label="label",
                    salting=salting.props["boiling_id"],
                    x=(salting.x[0], 0),
                    push_func=add_push,
                    axis=1,
                ):
                    with m.block():
                        m.block(
                            "salting_id_label",
                            size=(2, 2),
                            boiling_id=salting.props["boiling_id"],
                        )
                        m.block(
                            "salting_name_label",
                            size=(salting.size[0] - 2, 2),
                            boiling_label="boiling_label",
                        )

    # - Add frontend to output and return

    output["frontend"] = m.root

    return output


def test():
    print(wrap_frontend2(brynza_kg=10000, chanah_kg=10000)["schedule"])
    print(wrap_frontend2(brynza_kg=10000, chanah_kg=10000)["frontend"])


if __name__ == "__main__":
    test()
