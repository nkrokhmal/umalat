from flask import Blueprint

main = Blueprint("main", __name__)

from . import download, index
from .mozzarella import *
from .ricotta import *
