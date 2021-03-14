import random
from app.schedule_maker.models import *


def generate_random_boiling_plan(n=24, seed=12):
    random.seed(seed)

    sku_ids = range(62, 82)  # todo: take from table properly
    boiling_model_ids = range(9, 16)  # todo: take from table properly

    skus = [cast_model(RicottaSKU, sku_id) for sku_id in sku_ids]
    skus = [sku for sku in skus if sku.weight_netto]
    skus

    values = []
    for i in range(n):
        boiling_skus = []
        boiling_model = cast_model(RicottaBoiling, random.choice(boiling_model_ids))

        for _ in range(boiling_model.number_of_tanks):
            boiling_skus.append(
                random.choice(
                    [sku for sku in skus if boiling_model in sku.made_from_boilings]
                )
            )

        boiling_skus = list(sorted(boiling_skus, key=lambda sku: sku.name))
        for sku in boiling_skus:
            kg = sku.packing_speed * np.random.uniform(0.6, 0.8) / 3
            kg = custom_round(kg, 10, "ceil")
            values.append([i, sku, kg])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    return df
