import random
from app.schedule_maker.models import *


def generate_random_boiling_plan_mascarpone(n=3, seed=12):
    random.seed(seed)

    skus = fetch_all(MascarponeSKU)
    models = fetch_all(MascarponeBoiling)

    values = []
    for i in range(n):
        boiling_model = random.choice(models)

        for j in range(2):
            sku = random.choice(
                [sku for sku in skus if boiling_model in sku.made_from_boilings]
            )
            kg = sku.packing_speed * np.random.uniform(0.6, 0.8) / 2
            kg = custom_round(kg, 10, "ceil")
            values.append([i * 2 + j, sku, kg])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    return df


def generate_random_boiling_plan_cream_cheese(n=3, seed=12):
    random.seed(seed)

    skus = fetch_all(CreamCheeseSKU)
    models = fetch_all(CreamCheeseBoiling)

    values = []
    for i in range(n):
        boiling_model = random.choice(models)

        for j in range(2):
            sku = random.choice(
                [sku for sku in skus if boiling_model in sku.made_from_boilings]
            )
            kg = sku.packing_speed * np.random.uniform(0.6, 0.8) / 2
            kg = custom_round(kg, 10, "ceil")
            values.append([i * 2 + j, sku, kg])

    df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    return df
