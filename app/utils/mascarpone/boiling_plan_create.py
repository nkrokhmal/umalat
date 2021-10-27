from app.imports.runtime import *

from app.models import *
from app.utils.features.merge_boiling_utils import Boilings


def add_fields(result, type):
    if not result.empty:
        result["kg"] = result["plan"]
        result["name"] = result["sku"].apply(lambda sku: sku.name)
        result["boiling_type"] = result["sku"].apply(
            lambda sku: sku.made_from_boilings[0].to_str()
        )
        result["output"] = result["max_boiling_weight"]

        max_output = int(result["output"].max())
        if type == "mascarpone":
            result["fermentators"] = result["output"].apply(
                lambda x: "1-2" if x == max_output else "3-4"
            )
        else:
            result["fermentators"] = "-"

        result["coeff"] = result["sku"].apply(
            lambda sku: sku.made_from_boilings[0].output_coeff
        )
        result["kg"] = result["kg"] / result["coeff"]
        result["kg"] = result["kg"].apply(lambda x: math.ceil(x))

        result = result[
            [
                "id",
                "group",
                "output",
                "name",
                "boiling_type",
                "fermentators",
                "kg",
            ]
        ]

    return result


def mascarpone_boiling_plan_create(df):
    df["plan"] = df["plan"].apply(lambda x: round(x))
    df["percent"] = df["sku"].apply(lambda x: x.made_from_boilings[0].percent)
    df["is_lactose"] = df["sku"].apply(lambda x: x.made_from_boilings[0].is_lactose)
    df["weight"] = df["sku"].apply(lambda x: round(x.weight_netto))
    df["flavoring_agent"] = df["sku"].apply(
        lambda x: x.made_from_boilings[0].flavoring_agent
        if isinstance(x, MascarponeSKU) or isinstance(x, CreamCheeseSKU)
        else ""
    )
    df["group"] = df["sku"].apply(lambda x: x.group.name)

    mascarpone_result = handle_mascarpone(df)
    mascarpone_result = add_fields(mascarpone_result, "mascarpone")

    cream_cheese_result = handle_cream_cheese(df)
    cream_cheese_result = add_fields(cream_cheese_result, "cream_cheese")

    cream_result = handle_cream(df)
    cream_result = add_fields(cream_result, "cream")

    return mascarpone_result, cream_cheese_result, cream_result


def mascarpone_proceed_order(order, df, boilings, output_tons):
    print(order)
    df_filter = df[
        (df["group"] == order.group)
        & (
            order.flavoring_agent is None
            or df["flavoring_agent"] == order.flavoring_agent
        )
        & (
            df["is_lactose"] == order.is_lactose
        )
    ]
    print(df_filter)
    if not df_filter.empty:
        df_filter_groups = [group for _, group in df_filter.groupby("percent")]

        for df_filter_group in df_filter_groups:
            df_group_dict = df_filter_group.sort_values(
                by="weight",
                ascending=True,
            ).to_dict("records")

            boilings.add_group(
                df_group_dict,
            )
    return boilings


def cream_cheese_proceed_order(order, df, boilings):
    print(order)
    df_filter = df[
        (df["group"].isin(order.groups)) &
        (df["is_lactose"] == order.is_lactose) &
        (
            order.flavoring_agent is None
            or df["flavoring_agent"] == order.flavoring_agent
        )
    ].sort_values(
        by=["group", "percent"]
    )

    if not df_filter.empty:
        output_ton = (
            df_filter["sku"].apply(lambda x: x.made_from_boilings[0].output_ton).iloc[0]
        )
        boilings.init_iterator(output_ton)

        df_filter_groups = [group for _, group in df_filter.groupby("boiling_id")]
        for df_filter_group in df_filter_groups:
            df_group_dict = df_filter_group.to_dict("records")

            boilings.add_group(df_group_dict)
    return boilings


def handle_mascarpone(df):
    output_tons = sorted(
        list(
            set(
                [
                    x.output_ton
                    for x in db.session.query(MascarponeBoilingTechnology).all()
                ]
            )
        ),
        reverse=True,
    )
    output_tons = [max(output_tons) + min(output_tons), 2 * min(output_tons)]
    boilings_mascarpone = Boilings(max_iter_weight=output_tons)

    Order = collections.namedtuple("Collection", "flavoring_agent, is_lactose, group")
    orders = [
        Order("", True, "Маскарпоне"),
        Order("", False, "Маскарпоне"),
        Order("Шоколад", True, "Маскарпоне"),
    ]
    for order in orders:
        boilings_mascarpone = mascarpone_proceed_order(
            order, df, boilings_mascarpone, output_tons
        )
    boilings_mascarpone.finish()
    return pd.DataFrame(boilings_mascarpone.boilings)


def handle_cream(df):
    output_tons = [250]
    boilings_mascarpone = Boilings(max_iter_weight=output_tons)

    Order = collections.namedtuple("Collection", "flavoring_agent, is_lactose, group")
    orders = [
        Order("", True, "Сливки"),
    ]
    for order in orders:
        boilings_mascarpone = mascarpone_proceed_order(
            order, df, boilings_mascarpone, output_tons
        )
    boilings_mascarpone.finish()
    return pd.DataFrame(boilings_mascarpone.boilings)


def handle_cream_cheese(df):
    boilings_cream_cheese = Boilings()
    Order = collections.namedtuple("Collection", "flavoring_agent, is_lactose, groups")
    orders = [
        Order("", False, ["Кремчиз"]),
        Order("", True, ["Кремчиз"]),
        Order("Паприка", True, ["Кремчиз"]),
        Order("Томаты", True, ["Кремчиз"]),
        Order("Травы", True, ["Кремчиз"]),
        Order("", True, ["Робиола", "Творожный"]),
    ]
    for order in orders:
        boilings_cream_cheese = cream_cheese_proceed_order(
            order, df, boilings_cream_cheese
        )
    boilings_cream_cheese.finish()
    return pd.DataFrame(boilings_cream_cheese.boilings)
