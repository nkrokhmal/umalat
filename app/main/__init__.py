from flask import Blueprint

main = Blueprint("main", __name__)

from . import download, index, batch, login
from .mozzarella import *
from .ricotta import *
from .mascarpone import *
from .additional import *
from .butter import *
from .milkproject import *
from .adygea import *
from .approved import *
from .params import *
