import random
from app.schedule_maker.models import *


def generate_random_boiling_plan(n=24, seed=12):
    random.seed(seed)

    sku_ids = range(62, 82)  # todo: take from table properly
    boiling_model_ids = range(9, 16)  # todo: take from table properly

    skus = [cast_model(RicottaSKU, sku_id) for sku_id in sku_ids]
    skus

    values = []
    for i in range(n):
        boiling_skus = []
        boiling_model = cast_model(RicottaBoiling, random.choice(boiling_model_ids))

        n_boilings = random.choice([2, 3])
        for _ in range(n_boilings):
            boiling_skus.append(
                random.choice(
                    [sku for sku in skus if boiling_model in sku.made_from_boilings]
                )
            )

        boiling_skus = list(sorted(boiling_skus, key=lambda sku: sku.name))
        for sku in boiling_skus:
            values.append([i, sku, 1])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "volume"])

    return df
