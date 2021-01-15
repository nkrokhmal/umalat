from app.schedule_maker.models import *
from app.enum import LineName

# todo: refactor
def get_configuration_time(boiling_model, sku1, sku2):
    if all([boiling_model.line.name == LineName.SALT,
            sku1.form_factor != sku2.form_factor,
            cast_packer(sku1) == cast_packer(sku2),
            cast_packer(sku1).name == 'Ульма']):
        return 25
    elif sku1 == sku2:
        return 0
    else:
        return 5