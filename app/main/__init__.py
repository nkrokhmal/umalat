from flask import Blueprint


main = Blueprint('main', __name__)

from . import sku_plan, download, boiling_plan, schedule, sku, boiling, form_factor, views
# from . import views, sku, boiling, sku_plan, pouring, schedule, sku_plan_stats, boiling_plan, download, boiling_form_factor