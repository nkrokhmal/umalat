import os

os.environ["environment"] = "interactive"

from config import DebugConfig
from app.schedule_maker.departments.mozarella.algo import *
from app.schedule_maker.departments.mozarella.boiling_plan import read_boiling_plan

from utils_ak.interactive_imports import *
import warnings

warnings.filterwarnings("ignore")
from utils_ak.loguru import configure_loguru_stdout


def test1():
    configure_loguru_stdout("DEBUG")

    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path("app/data/inputs/sample_boiling_plan.xlsx")
    )
    boiling_plan_df = boiling_plan_df[
        boiling_plan_df["boiling"].apply(lambda b: b.line.name == LineName.SALT)
    ]

    for _, grp in boiling_plan_df.groupby("group_id"):
        grp["packing_speed"] = grp["sku"].apply(lambda sku: sku.packing_speed)
        print(grp[["sku_name", "kg"]])
        boilings = make_boilings_parallel_dynamic(grp)
        for boiling in boilings:
            print(boiling)
            mp = boiling["melting_and_packing"]
            mp.props.update(x=(0, 0))


def test2():
    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path("app/data/inputs/sample_boiling_plan.xlsx")
    )

    mark_consecutive_groups(boiling_plan_df, "boiling", "boiling_group")

    grp = boiling_plan_df[boiling_plan_df["boiling_group"] == 3]

    grp["packing_speed"] = grp["sku"].apply(lambda sku: sku.packing_speed)
    display(grp)
    boilings = make_boilings_parallel_dynamic(grp)
    for boiling in boilings:
        print(boiling.props["boiling_id"])
        mp = boiling["melting_and_packing"]
        mp.props.update(x=(0, 0))
        display(mp)


def test3():
    boiling_plan_df = read_boiling_plan(
        DebugConfig.abs_path("app/data/inputs/sample_boiling_plan.xlsx")
    )

    boiling_df = boiling_plan_df[
        boiling_plan_df["bff"] == cast_mozarella_form_factor(14)
    ]
    boiling_df["sku_name"] = boiling_df["sku"].apply(lambda sku: sku.name)

    values = []
    for _, grp in boiling_df.groupby(["packing_team_id", "sku_name"]):
        value = grp.iloc[0]
        value["kg"] = grp["kg"].sum()
        values.append(value)

    if len(boiling_df) > 0:
        boiling_df = pd.DataFrame(values)
        boiling_df.pop("sku_name")

        boiling_df["left"] = boiling_df["kg"]
        boiling_df["packing_speed"] = boiling_df["sku"].apply(
            lambda sku: sku.packing_speed
        )

        make_mpp(boiling_df, 850)
        print(boiling_df)


if __name__ == "__main__":
    test1()
    # test2()
    # test3()