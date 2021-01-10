from flask import Blueprint


main = Blueprint('main', __name__)


from . import views, sku, boiling, sku_plan, pouring, schedule, sku_plan_stats, generate_boiling_plan, download, boiling_form_factor