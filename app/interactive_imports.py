import os
import sys

os.environ["mode"] = 'dev'

sys.path.append(os.environ.get('UTILS_PATH'))
from utils_ak.interactive_imports import *

from app.schedule_maker import *
