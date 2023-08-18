import collections
import copy
import glob
import inspect
import io
import itertools
import math
import os
import pickle
import random
import re
import shutil
import sys
import time as time_lib
import traceback
import types
import warnings

from datetime import datetime, time, timedelta
from pprint import pprint
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Type, TypeVar, Union

import flask
import flask_bootstrap
import flask_migrate
import flask_pagedown
import flask_rq2
import flask_sqlalchemy
import notifiers
import numpy as np
import openpyxl
import pandas as pd
import pycel
import pydantic
import telebot
import tqdm
import ujson as json
import yaml

from icecream import ic
from loguru import logger
from notifiers.logging import NotificationHandler
from pydantic import Field
from utils_ak.block_tree.block import Block
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.parallelepiped_block import ParallelepipedBlock
from utils_ak.block_tree.pushers.iterative import AxisPusher, IterativePusher, ShiftPusher
from utils_ak.block_tree.pushers.pushers import add_push, push, simple_push
from utils_ak.block_tree.validation import ClassValidator, disjoint_validator, validate_disjoint_by_axis
from utils_ak.builtin.collection import (
    crop_to_chunks,
    delistify,
    iter_get,
    remove_duplicates,
    remove_neighbor_duplicates,
)
from utils_ak.builtin.none import is_none_like
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.color.color import cast_color
from utils_ak.iteration.simple_iterator import SimpleIterator, iter_pairs, iter_sequences
from utils_ak.lazy_tester.lazy_tester_class import lazy_tester
from utils_ak.numeric.numeric import custom_round
from utils_ak.numeric.types import cast_int, is_float, is_float_like, is_int, is_int_like
from utils_ak.openpyxl.openpyxl_tools import (
    cast_workbook,
    cast_worksheet,
    draw_merged_cell,
    draw_sheet_sequence,
    init_workbook,
    read_merged_cells_df,
    set_active_sheet,
    set_border_grid,
    set_dimensions,
    set_zoom,
)
from utils_ak.os.os_tools import makedirs, open_file_in_os
from utils_ak.pandas.pandas_tools import df_to_ordered_tree, mark_consecutive_groups, split_into_sum_groups
from utils_ak.portion.portion_tools import calc_interval_length, cast_interval
from utils_ak.split_file.split_file import SplitFile

from app.enum import DepartmentName, LineName
from app.globals import ERROR, basedir
from app.imports import utils
from app.models import (
    SKU,
    AdygeaBoiling,
    AdygeaBoilingTechnology,
    AdygeaFormFactor,
    AdygeaLine,
    AdygeaSKU,
    Boiling,
    ButterBoiling,
    ButterBoilingTechnology,
    ButterFormFactor,
    ButterLine,
    ButterSKU,
    CreamCheeseBoiling,
    CreamCheeseBoilingTechnology,
    CreamCheeseFermentator,
    CreamCheeseFormFactor,
    CreamCheeseLine,
    CreamCheeseSKU,
    FormFactor,
    Group,
    Line,
    MascarponeBoiling,
    MascarponeBoilingTechnology,
    MascarponeFormFactor,
    MascarponeLine,
    MascarponeSKU,
    MascarponeSourdough,
    MilkProjectBoiling,
    MilkProjectBoilingTechnology,
    MilkProjectFormFactor,
    MilkProjectLine,
    MilkProjectSKU,
    MozzarellaBoiling,
    MozzarellaBoilingTechnology,
    MozzarellaCoolingTechnology,
    MozzarellaFormFactor,
    MozzarellaLine,
    MozzarellaSKU,
    RicottaAnalysisTechnology,
    RicottaBoiling,
    RicottaBoilingTechnology,
    RicottaFormFactor,
    RicottaLine,
    RicottaSKU,
    User,
    cast_model,
    fetch_all,
)
from app.scheduler.adygea.properties import AdygeaProperties
from app.scheduler.butter.properties import ButterProperties
from app.scheduler.frontend import draw_excel_frontend, prepare_schedule_worksheet
from app.scheduler.header import wrap_header
from app.scheduler.load_properties import load_properties
from app.scheduler.load_schedules import load_schedules
from app.scheduler.mascarpone.properties import MascarponeProperties
from app.scheduler.milk_project.properties import MilkProjectProperties
from app.scheduler.mozzarella.properties import MozzarellaProperties
from app.scheduler.parsing import load_cells_df, parse_block
from app.scheduler.parsing_new.group_intervals import basic_criteria
from app.scheduler.parsing_new.parse_time import cast_time_from_hour_label
from app.scheduler.parsing_new.parsing import parse_line
from app.scheduler.ricotta.properties import RicottaProperties
from app.scheduler.submit import submit_schedule
from app.scheduler.time import cast_human_time, cast_t, cast_time, parse_time
from config import config
