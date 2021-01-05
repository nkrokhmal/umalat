from app.schedule_maker.models import *


# todo: take from parameters
def get_configuration_time(boiling_model, sku1, sku2):
    # todo: make properly
    if boiling_model.boiling_type == 'salt' and sku1.weight_form_factor != sku2.weight_form_factor and cast_packer(sku1) == cast_packer(sku2):
        return 25
    elif sku1 == sku2:
        return 0
    else:
        return 5