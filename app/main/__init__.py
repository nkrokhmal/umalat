from flask import Blueprint


main = Blueprint('main', __name__)


from . import views, sku, boiling, parse_request, pouring, schedule, generate_sku_plan, generate_boiling_plan