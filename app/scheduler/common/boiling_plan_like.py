from typing import Union

import pandas as pd

from openpyxl import Workbook


BoilingPlanLike = str | Workbook | pd.DataFrame
