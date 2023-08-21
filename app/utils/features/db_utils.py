from app.models.basic import SKU


def get_sku_by_name(skus: list[SKU], name: str) -> SKU | None:
    return next((x for x in skus if x.name == name), None)


def sku_is_rubber(skus: list[SKU], name: str) -> bool:
    sku = get_sku_by_name(skus, name)
    if sku is None:
        return False

    return "Терка" in sku.form_factor.name
