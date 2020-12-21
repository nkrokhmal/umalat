import os
import sys

os.environ["mode"] = 'dev'

sys.path.append(os.environ.get('UTILS_PATH'))
from utils_ak.interactive_imports import *

from app.schedule_maker.utils.time import *
from app.schedule_maker.utils.block import *
from app.schedule_maker.utils.color import *
from app.schedule_maker.utils.drawing import *
from app.schedule_maker.utils.interval import *
from app.schedule_maker.blocks import *
from app.schedule_maker.algo import *
from app.schedule_maker.style import *
from app.schedule_maker.validation import *
from app.schedule_maker.frontend import *
