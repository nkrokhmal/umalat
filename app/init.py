import os
from utils_ak.os import makedirs
from config import DebugConfig

for local_path in [
    DebugConfig.UPLOAD_TMP_FOLDER,
    DebugConfig.STATS_FOLDER,
    DebugConfig.BOILING_PLAN_FOLDER,
    DebugConfig.SKU_PLAN_FOLDER,
    DebugConfig.SCHEDULE_PLAN_FOLDER,
]:
    makedirs(DebugConfig.abs_path(local_path) + "/")

for local_path in [
    DebugConfig.TEMPLATE_BOILING_PLAN,
    DebugConfig.IGNORE_SKU_FILE,
]:
    makedirs(DebugConfig.abs_path(local_path))
