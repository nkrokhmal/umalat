import os
import sys

os.environ['environment'] = 'interactive'

sys.path.append(os.environ.get('UTILS_PATH'))
from utils_ak.interactive_imports import *

from app.schedule_maker import *

from config import basedir
set_global_db()