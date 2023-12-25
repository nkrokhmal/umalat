import itertools
import math

from more_itertools import mark_ends
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis
from utils_ak.builtin.collection import iter_get
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.iteration.simple_iterator import iter_sequences
from utils_ak.pandas import mark_consecutive_groups
from utils_ak.portion.portion_tools import cast_interval

from app.lessmore.utils.get_repo_path import get_repo_path
from app.models import AdygeaLine, BrynzaLine, Washer, cast_model
from app.scheduler.adygea.make_schedule._boilings import make_boiling, make_cleaning, make_lunch, make_preparation
from app.scheduler.adygea.to_boiling_plan.to_boiling_plan import (
    to_boiling_plan,
    to_boiling_plan as to_boiling_plan_adygea,
)
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.brynza.to_boiling_plan import to_boiling_plan as to_boiling_plan_brynza
from app.scheduler.time_utils import cast_t, cast_time


def make_packing_schedule(
    boiling_plan: BoilingPlanLike,
    start_time="07:00",
):
    # - Alias dataframes

    df1 = to_boiling_plan_brynza(boiling_plan)
    df2 = to_boiling_plan_adygea(boiling_plan)

    # - Make schedule

    brynza_line = cast_model(cls=BrynzaLine, obj="Брынза")

    start_t = cast_t(start_time)

    m = BlockMaker("schedule")

    m.row("preparation", size=7)

    # boiling_technology = df1.iloc[0]["boiling"].boiling_technologies[0]

    # build label for brynza
    mark_consecutive_groups(df1, key="boiling", groups_key="boiling_num")
    values = []
    for i, grp in list(df1.groupby("boiling_num")):
        boiling = grp.iloc[0]["boiling"]
        sku = grp.iloc[0]["sku"]
        values.append(f"{sku.name} - {round(grp['kg'].sum())}кг")
    label = ", ".join(values)

    m.row(
        "packing_brynza",
        size=round((df1["kg"] / df1["sku"].apply(lambda sku: sku.packing_speed)).sum() * 12),
        label=label,
    )
    m.row("small_cleaning", size=5)
    m.row("labelling", size=14)

    df2["boiling_type"] = df2["boiling"].apply(lambda boiling: str(boiling.weight_netto) + "-" + str(boiling.percent))

    mark_consecutive_groups(df2, key="boiling_type", groups_key="boiling_type_num")

    for is_first, is_last, (i, grp) in mark_ends(list(df2.groupby("boiling_type_num"))):
        boiling = grp.iloc[0]["boiling"]
        total_kg = grp["kg"].sum()
        packing_speed = grp["sku"].iloc[0].packing_speed  # note: packing_speed is the same for all skus in adygea

        # crop to pieces of 200kg

        pieces_kg = [200] * int(total_kg / 200) + [total_kg - 200 * int(total_kg / 200)]
        pieces_kg = [piece_kg for piece_kg in pieces_kg if abs(piece_kg) > 0.1]

        for _is_first, _is_last, piece_kg in mark_ends(pieces_kg):
            m.row(
                "packing_adygea",
                size=round(piece_kg / packing_speed * 12),
                label=f"Адыгейский {boiling.weight_netto}, {round(piece_kg)}кг",
            )
            if not _is_last:
                m.row("packing_configuration", size=1)

        if not is_last:
            m.row("packing_configuration", size=1)

    m.row("cleaning", size=12)

    return {
        "schedule": m.root,
        "brynza_boiling_plan_df": df1,
        "adygea_boiling_plan_df": df2,
    }


def test():
    # - Read boiling plan

    print(
        make_packing_schedule(
            boiling_plan=f"/Users/arsenijkadaner/FileApps/coding_projects/umalat/app/data/static/samples/by_department/milk_project/2023-11-19 План по варкам милкпроджект Новый.xlsx"
        )
    )


if __name__ == "__main__":
    test()
