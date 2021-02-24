from flask import Blueprint

main = Blueprint('main', __name__)


from . import download, views
from .mozzarella import *