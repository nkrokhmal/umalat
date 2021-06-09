from app.imports.runtime import *
from app.models import *
from app.scheduler.butter.boiling_plan.saturate import saturate_boiling_plan


def generate_random_boiling_plan(n=10, seed=12):
    random.seed(seed)
    np.random.seed(seed)

    skus = fetch_all(MilkProjectSKU)
    skus = [sku for sku in skus if sku.weight_netto]

    models = fetch_all(MilkProjectBoiling)

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
            kg = 100
            # todo soon: del
            if len(sku.made_from_boilings) > 1:
                continue
            values.append([i, sku, kg])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    df = saturate_boiling_plan(df)
    return df
