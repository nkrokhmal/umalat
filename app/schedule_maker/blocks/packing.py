from app.schedule_maker.models import *


def get_configuration_time(boiling_model, sku1, sku2):
    # todo: test
    if all([boiling_model.boiling_type == 'salt',
            sku1.weight_form_factor != sku2.weight_form_factor,
            cast_packer(sku1) == cast_packer(sku2),
            cast_packer(sku1).name == 'Ульма']):
        return 25
    elif sku1 == sku2:
        return 0
    else:
        return 5