from flask import Blueprint

main = Blueprint('main', __name__)


from . import download, boiling_plan_fast, views, schedule
from .mozzarella import params, params_sku, params_boiling_technology
# from . import download, schedule, sku, boiling, form_factor, views, sku_plan, boiling_plan, boiling_plan_fast
