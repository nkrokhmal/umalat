from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.enum import LineName


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
        df.columns = ['batch_id', 'boiling_params', 'sku', 'kg', 'packing_team_id']

        # remove separators and empty lines
        df = df[df['sku'] != '-']
        df = df[~df['kg'].isnull()]

        # add line name to boiling_params
        df['boiling_params'] = (LineName.WATER if ws_name == 'Вода' else LineName.SALT) + ',' + df['boiling_params']
        dfs.append(df)

    df = pd.concat(dfs)
    df['sku'] = df['sku'].apply(cast_sku)

    df['boiling'] = df['boiling_params'].apply(cast_boiling)

    # set boiling form factors
    df['ff'] = df['sku'].apply(lambda sku: sku.form_factor)

    # remove Терка from form_factors
    df['bff'] = df['ff'].apply(lambda ff: ff if ff.name != 'Терка' else None)

    # fill Терка empty form factor values
    df['bff'] = df['bff'].fillna(method='ffill')
    df['bff'] = df['bff'].fillna(method='bfill')

    # validate single boiling
    for _, grp in df.groupby('batch_id'):
        assert len(grp['boiling'].unique()) == 1, "Only one boiling allowed inside a group"

    # validate kilograms
    for _, grp in df.groupby('batch_id'):
        boiling_model = grp.iloc[0]['boiling']
        assert grp['kg'].sum() % boiling_model.line.output_per_ton == 0, "Fill enough kilograms for the boiling"

    return df.reset_index(drop=True)
