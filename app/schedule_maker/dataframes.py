from utils_ak.interactive_imports import *
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

        # collect header
        header = [ws.cell(1, i).value for i in range(1, 100) if ws.cell(1, i).value]

        for i in range(2, 200):
            if not ws.cell(i, 1).value:
                continue
            values.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])

        df = pd.DataFrame(values, columns=header)
        df = df[['Номер партии', 'Тип варки', 'SKU', 'КГ', 'Номер команды']]
        # todo: boiling_full_type -> boiling_type, boiling_type -> boiling_line_type
        df.columns = ['batch_id', 'boiling_params', 'sku', 'kg', 'packing_team_id']

        # remove separators and empty lines
        df = df[df['sku'] != '-']
        df = df[~df['kg'].isnull()]

        df['boiling_line_type'] = 'water' if ws_name == 'Вода' else 'salt'
        dfs.append(df)

    df = pd.concat(dfs)
    df['sku'] = df['sku'].apply(cast_sku)

    df['boiling_full_type'] = df['boiling_line_type'] + ',' + df['boiling_params']
    df['boiling'] = df['boiling_full_type'].apply(cast_boiling)

    # todo: check that all boiling groups have the same boiling
    return df.reset_index(drop=True)


