from app.imports.runtime import *
from app.models import *
from app.utils.mozzarella.boiling_plan_create import get_boiling_form_factor


def prepare_schedule_json(schedule_json, cleanings):
    for x in schedule_json["children"][0]["children"]:
        if x["cls"] == "boiling":
            x["props"]["boiling_group_df"]["time"] = x["props"]["x"][0]

    schedule_df = pd.concat(
        [x["props"]["boiling_group_df"] for x in schedule_json["children"][0]["children"] if x["cls"] == "boiling"]
    )
    schedule_df["cleaning"] = np.nan
    for cleaning in cleanings:
        for i in range(schedule_df.shape[0] - 1):
            if (schedule_df.iloc[i]["time"] < cleaning["props"]["x"][0]) and (
                schedule_df.iloc[i + 1]["time"] >= cleaning["props"]["x"][0]
            ):
                schedule_df.loc[i, "cleaning"] = (
                    "Длинная мойка" if cleaning["props"]["cleaning_type"] == "full" else "Короткая мойка"
                )

    schedule_df["id"] = schedule_df["group_id"]
    schedule_df["name"] = schedule_df["sku_name"]
    schedule_df["packer"] = schedule_df["sku"].apply(lambda sku: sku.packers_str)
    schedule_df["boiling_form_factor"] = schedule_df["sku"].apply(lambda sku: get_boiling_form_factor(sku))
    schedule_df["form_factor"] = schedule_df["sku"].apply(lambda x: x.form_factor.name)
    schedule_df["group"] = schedule_df["sku"].apply(lambda x: x.group.name)
    schedule_df["boiling_configuration"] = schedule_df["boiling_volumes"].apply(lambda x: x[0])
    schedule_df["boiling_type"] = schedule_df["boiling"].apply(lambda x: x.boiling_type)
    schedule_df["boiling_volume"] = np.where(
        schedule_df["boiling_type"] == "salt",
        cast_model(MozzarellaLine, LineName.SALT).output_kg,
        cast_model(MozzarellaLine, LineName.WATER).output_kg,
    )
    schedule_df["boiling_name"] = schedule_df["boiling"].apply(lambda b: b.to_str())
    schedule_df["boiling_id"] = schedule_df["boiling"].apply(lambda b: b.id)
    schedule_df["team_number"] = schedule_df["packing_team_id"]
    schedule_df["kg"] = schedule_df["original_kg"]

    schedule_df = schedule_df[
        [
            "id",
            "boiling_id",
            "boiling_name",
            "boiling_volume",
            "group",
            "form_factor",
            "boiling_form_factor",
            "packer",
            "name",
            "kg",
            "team_number",
            "boiling_configuration",
            "time",
            "cleaning",
        ]
    ]
    return schedule_df
