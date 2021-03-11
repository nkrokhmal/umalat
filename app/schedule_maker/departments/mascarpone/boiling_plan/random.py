import random
from app.schedule_maker.models import *


def generate_random_boiling_plan(n=3, seed=12):
    random.seed(seed)

    mascarpone_ids = range(82, 91)  # todo: take from table properly
    mascarpone_model_ids = range(16, 20)  # todo: take from table properly
    sku_ids = mascarpone_ids
    boiling_model_ids = mascarpone_model_ids

    skus = [cast_model(MascarponeSKU, sku_id) for sku_id in sku_ids]
    skus

    values = []
    for i in range(n):
        boiling_model = cast_model(MascarponeBoiling, random.choice(boiling_model_ids))

        boiling_skus = []
        for _ in range(2):
            boiling_skus.append(
                random.choice(
                    [sku for sku in skus if boiling_model in sku.made_from_boilings]
                )
            )

        for sku in boiling_skus:
            values.append([i, sku, 10])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "volume"])
    return df
