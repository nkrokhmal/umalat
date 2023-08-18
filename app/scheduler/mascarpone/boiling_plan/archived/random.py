def _generate_random_boiling_group(sku_model, boiling_model, n=3):
    skus = fetch_all(sku_model)
    models = fetch_all(boiling_model)

    values = []
    for i in range(n):
        boiling_model = random.choice(models)

        for j in range(2):
            sku = random.choice([sku for sku in skus if boiling_model in sku.made_from_boilings])
            kg = sku.packing_speed * np.random.uniform(0.6, 0.8) / 2
            kg = custom_round(kg, 10, "ceil")
            values.append([i * 2 + j, sku, kg])

    return pd.DataFrame(values, columns=["batch_id", "sku", "kg"])


def generate_random_boiling_plan(n_groups=4, seed=3):
    random.seed(seed)
    np.random.seed(seed)

    dfs = []
    for group_type in random.choices(["Mascarpone", "CreamCheese"], k=n_groups):
        sku_model = globals()[group_type + "SKU"]
        boiling_model = globals()[group_type + "Boiling"]
        df = _generate_random_boiling_group(sku_model, boiling_model)
        dfs.append(df)

    res = pd.concat(dfs, axis=0)
    res = saturate_boiling_plan(res)
    return res
