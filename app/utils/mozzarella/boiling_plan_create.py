from app.imports.runtime import *

from app.utils.features.merge_boiling_utils import Boilings
from app.models import cast_mozarella_boiling


def boiling_plan_create(df):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["boiling_type"] = df["boiling_id"].apply(
        lambda boiling_id: cast_mozarella_boiling(boiling_id).boiling_type
    )
    df["weight"] = df["sku"].apply(
        lambda x: x.form_factor.relative_weight + 30
        if "Терка" in x.form_factor.name
        else x.form_factor.relative_weight
    )
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["is_lactose"] = df["sku"].apply(lambda x: x.made_from_boilings[0].is_lactose)
    df["ferment"] = df["sku"].apply(lambda x: x.made_from_boilings[0].ferment)
    df["pack_weight"] = df["sku"].apply(lambda x: x.weight_netto)
    df["group"] = df["sku"].apply(lambda x: x.group.name)

    water, boiling_number = handle_water(df[df["boiling_type"] == "water"])
    salt, boiling_number = handle_salt(
        df[df["boiling_type"] == "salt"], boiling_number=boiling_number + 1
    )

    result = pd.concat([water, salt])
    result["kg"] = result["plan"]
    result["boiling"] = result["boiling_id"].apply(lambda x: cast_mozarella_boiling(x))
    result["name"] = result["sku"].apply(lambda sku: sku.name)
    result["boiling_name"] = result["boiling"].apply(lambda b: b.to_str())
    result["boiling_volume"] = np.where(result["boiling_type"] == "salt", 850, 1000)
    result["packer"] = result["sku"].apply(lambda sku: sku.packers_str)
    result["form_factor"] = result["sku"].apply(
        lambda sku: sku.form_factor.weight_with_line
    )
    result["boiling_form_factor"] = result["sku"].apply(
        lambda sku: get_boiling_form_factor(sku)
    )
    result = result[
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
        ]
    ]
    return result


def handle_water(df, max_weight=1000, min_weight=1000, portion=100, boiling_number=1):
    boilings_water = Boilings(
        max_weight=max_weight, min_weight=min_weight, boiling_number=boiling_number
    )
    orders = [
        (None, 3.3, "Альче", None),
        (True, 3.3, "Сакко", "Фиор Ди Латте"),
        (True, 3.6, "Альче", "Фиор Ди Латте"),
        (True, 3.6, "Альче", "Чильеджина"),
        (True, 3.3, "Альче", "Чильеджина"),
        (True, 3.3, "Сакко", "Чильеджина"),
    ]

    for order in orders:
        df_filter = df[
            (order[0] is None or df["is_lactose"] == order[0])
            & (df["percent"] == order[1])
            & (df["ferment"] == order[2])
            & (order[3] is None or df["group"] == order[3])
        ]
        # df_filter = df_filter.sort_values(by='plan', ascending=True)

        if not order[0]:
            df_filter_chl = df_filter[
                (df_filter["group"] == "Чильеджина") & (~df_filter["is_lactose"])
            ].sort_values(by=["weight", "plan"], ascending=[False, True])

            df_filter_fdl = df_filter[
                (df_filter["group"] == "Фиор Ди Латте") & (~df_filter["is_lactose"])
            ].sort_values(by=["weight", "plan"], ascending=[False, True])

            df_filter_oth = df_filter[df_filter["is_lactose"]].sort_values(
                by=["weight", "plan"], ascending=[False, True]
            )

            total_sum_without_lactose = df_filter[(~df_filter["is_lactose"])][
                "plan"
            ].sum()
            total_sum = df_filter["plan"].sum()

            if total_sum // max_weight == total_sum_without_lactose // max_weight:
                if (df_filter_chl["plan"].sum() < portion) and (
                    df_filter_oth["plan"].sum() < portion
                ):
                    order = [df_filter_chl, df_filter_oth, df_filter_fdl]
                elif (df_filter_chl["plan"].sum() < portion) and (
                    df_filter_oth["plan"].sum() > portion
                ):
                    order = [df_filter_chl, df_filter_fdl, df_filter_oth]
                elif (df_filter_chl["plan"].sum() > portion) and (
                    df_filter_oth["plan"].sum() < portion
                ):
                    order = [df_filter_oth, df_filter_fdl, df_filter_chl]
                else:
                    order = [df_filter_fdl, df_filter_chl, df_filter_oth]
                df_filter_dict = pd.concat(order).to_dict("records")
                boilings_water.add_group(df_filter_dict)
            else:
                if df_filter_chl["plan"].sum() < 100:
                    order = [df_filter_chl, df_filter_fdl]
                else:
                    order = [df_filter_fdl, df_filter_chl]

                df_filter_dict = pd.concat(order).to_dict("records")
                df_filter_dict_lactose = df_filter_oth.to_dict("records")
                boilings_water.add_group(df_filter_dict)
                boilings_water.add_group(df_filter_dict_lactose)
        else:
            df_filter_dict = df_filter.sort_values(
                by=["weight", "pack_weight", "plan"], ascending=[False, False, True]
            ).to_dict("records")
            boilings_water.add_group(df_filter_dict)

    boilings_water.finish()
    return pd.DataFrame(boilings_water.boilings), boilings_water.boiling_number


def handle_salt(df, max_weight=850, min_weight=850, boiling_number=1):
    boilings = Boilings(max_weight=850, min_weight=850, boiling_number=boiling_number)

    for weight, df_grouped_weight in df.groupby("weight"):
        for boiling_id, df_grouped_boiling_id in df_grouped_weight.groupby(
            "boiling_id"
        ):
            new = True
            for group, df_grouped in df_grouped_boiling_id.groupby("group"):
                rubber_sku_exist = any(
                    [
                        x
                        for x in df_grouped.to_dict("records")
                        if "Терка" in x["sku"].form_factor.name
                    ]
                )
                if rubber_sku_exist:
                    df_grouped_sul = [
                        x
                        for x in df_grouped.to_dict("records")
                        if x["sku"].form_factor.name == "Терка Сулугуни"
                    ]
                    df_grouped_moz = [
                        x
                        for x in df_grouped.to_dict("records")
                        if x["sku"].form_factor.name == "Терка Моцарелла"
                    ]

                    boilings.add_group(df_grouped_sul, new=True)
                    boilings.add_group(df_grouped_moz, new=True)
                    new = True
                else:
                    df_grouped_dict = df_grouped.sort_values(
                        by=["weight", "pack_weight", "plan"],
                        ascending=[True, False, True],
                    ).to_dict("records")
                    boilings.add_group(df_grouped_dict, new=new)
                    new = False

    boilings.finish()
    return pd.DataFrame(boilings.boilings), boilings.boiling_number


def get_boiling_form_factor(sku):
    if "терка" not in sku.form_factor.name.lower():
        return sku.form_factor.weight_with_line
    elif "хачапури" in sku.name.lower():
        return "{}: {}".format(sku.line.name_short, 370)
    else:
        return "{}: {}".format(sku.line.name_short, 460)
