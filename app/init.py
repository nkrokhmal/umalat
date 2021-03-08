import os
from utils_ak.os import makedirs
from config import basedir

data_path = os.path.join(basedir, "app", "data")

makedirs(os.path.join(data_path, "sku_plan/"))
makedirs(os.path.join(data_path, "schedule_plan/"))
