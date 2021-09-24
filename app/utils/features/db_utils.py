def get_sku_by_name(skus, name):
    sku = [x for x in skus if x.name == name]
    if any(sku):
        return sku[0]
    else:
        return None


def sku_is_rubber(skus, name):
    sku = [x for x in skus if x.name == name]
    if any(sku):
        return "Терка" in sku[0].form_factor.name
    else:
        return False