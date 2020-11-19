import pandas as pd
from openpyxl import Workbook
from datetime import datetime
import openpyxl as opx
from openpyxl.styles import Alignment
from openpyxl.styles import PatternFill
import json
WB = opx.load_workbook(r'2020.11.18 schedule_template.xlsx')
SHEET = WB.worksheets[0]