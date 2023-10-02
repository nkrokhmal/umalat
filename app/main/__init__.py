from flask import Blueprint


main = Blueprint("main", __name__)

from app.main.adygea import *

from . import batch, download, index, login
from .additional import *
from .approved import *
from .butter import *
from .contour_washers import *
from .departments_schedule import *
from .mascarpone import *
from .milk_project import *
from .mozzarella import *
from .params import *
from .ricotta import *
