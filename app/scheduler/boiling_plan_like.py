from typing import Union

import pandas as pd

from openpyxl import Workbook


BoilingPlanLike = Union[str, Workbook, pd.DataFrame]
