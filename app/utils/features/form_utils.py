def default_form_value(form, val):
    for key, value in dict(form.choices).items():
        if value == val:
            form.default = key


def get_choice_data(f):
    return dict(f.choices).get(f.data)


def fill_ricotta_sku_from_form(sku, form):
    if form.boiling.data != -1:
        sku.made_from_boilings = [
            x for x in form.boilings if x.to_str() == get_choice_data(form.boiling)
        ]

    if form.group.data != -1:
        sku.group = [x for x in form.groups if x.name == get_choice_data(form.group)][0]

    return sku


def fill_mascarpone_sku_from_form(sku, form):
    if form.boiling.data != -1:
        sku.made_from_boilings = [
            x for x in form.boilings if x.to_str() == get_choice_data(form.boiling)
        ]

    if form.group.data != -1:
        sku.group = [x for x in form.groups if x.name == get_choice_data(form.group)][0]

    return sku


def fill_butter_sku_from_form(sku, form):
    return fill_mascarpone_sku_from_form(sku, form)


def fill_milk_project_sku_from_form(sku, form):
    return fill_mascarpone_sku_from_form(sku, form)


def fill_adygea_sku_from_form(sku, form):
    return fill_mascarpone_sku_from_form(sku, form)


def fill_mozzarella_sku_from_form(sku, form):
    if form.boiling.data != -1:
        sku.made_from_boilings += [
            x for x in form.boilings if x.to_str() == get_choice_data(form.boiling)
        ]

    if form.group.data != -1:
        sku.group = [x for x in form.groups if x.name == get_choice_data(form.group)][0]

    if form.packer.data != -1:
        sku.packers = [
            x for x in form.packers if x.name == get_choice_data(form.packer)
        ]

    if form.pack_type.data != -1:
        sku.pack_type = [
            x for x in form.pack_types if x.name == get_choice_data(form.pack_type)
        ][0]

    if form.line.data != -1:
        sku.line = [x for x in form.lines if x.name == get_choice_data(form.line)][0]

    if form.form_factor.data != -1:
        sku.form_factor = [
            x
            for x in form.form_factors
            if x.full_name == get_choice_data(form.form_factor)
        ][0]

    return sku
