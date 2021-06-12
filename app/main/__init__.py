from flask import Blueprint

main = Blueprint("main", __name__)

from . import download, index, batch, login
from .mozzarella import *
from .ricotta import *
from .mascarpone import *
from .additional import *
