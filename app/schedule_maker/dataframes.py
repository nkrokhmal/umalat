import openpyxl
import pandas as pd

from utils_ak.openpyxl import *
from app.schedule_maker.models import *


def read_boiling_plan(wb_obj):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = cast_workbook(wb_obj)

    dfs = []

    for ws_name in ['Вода', 'Соль']:
        ws = wb[ws_name]
        values = []
        for i in range(2, 200):
            if not ws.cell(i, 1).value:
                continue
            values.append([ws.cell(i, j).value for j in [1, 2, 6, 7, 9]])
        df = pd.DataFrame(values, columns=['boiling', 'id', 'sku', 'kg', 'packing_team_id'])  # first value is header
        df = df[df['boiling'] != '-']
        df = df[~df['kg'].isnull()]
        df = df[['id', 'boiling', 'sku', 'kg', 'packing_team_id']]  # reorder
        if dfs:
            df['id'] = df['id'] + dfs[-1].iloc[-1]['id']
        dfs.append(df)

    df = pd.concat(dfs)
    boiling_plan_df = df
    boiling_plan_df['sku'] = boiling_plan_df['sku'].apply(cast_sku)
    boiling_plan_df['boiling'] = boiling_plan_df['sku'].apply(lambda sku: sku.boilings[0])

    return boiling_plan_df.reset_index(drop=True)
