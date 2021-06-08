from app.imports.runtime import *
from app.models import *
from app.scheduler.butter.boiling_plan.saturate import saturate_boiling_plan


def generate_random_boiling_plan(n=3, seed=12):
    random.seed(seed)
    np.random.seed(seed)

    skus = fetch_all(ButterSKU)
    skus = [sku for sku in skus if sku.weight_netto]

    models = fetch_all(ButterBoiling)

    values = []
    for i in range(n):
        boiling_skus = []
        boiling_model = random.choice(models)

        for _ in range(4):
            boiling_skus.append(
                random.choice(
                    [sku for sku in skus if boiling_model in sku.made_from_boilings]
                )
            )
        boiling_skus = list(sorted(boiling_skus, key=lambda sku: sku.name))
        for sku in boiling_skus:
            kg = sku.packing_speed * np.random.uniform(0.6, 0.8) / 3
            kg = utils.custom_round(kg, 10, "ceil")
            values.append([i, sku, kg])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    df = saturate_boiling_plan(df)
    return df
