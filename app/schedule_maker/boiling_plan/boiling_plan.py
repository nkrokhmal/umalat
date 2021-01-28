from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.enum import LineName
from .saturate import saturate_boiling_plan

def read_boiling_plan(wb_obj, saturate=True):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = cast_workbook(wb_obj)

    dfs = []

    for ws_name in ['Вода', 'Соль']:
        line = cast_line(LineName.WATER) if ws_name == 'Вода' else cast_line(LineName.SALT)
        default_boiling_volume = line.output_ton

        ws = wb[ws_name]
        values = []

        # collect header
        header = [ws.cell(1, i).value for i in range(1, 100) if ws.cell(1, i).value]

        for i in range(2, 200):
            if not ws.cell(i, 2).value:
                continue
            values.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])

        df = pd.DataFrame(values, columns=header)
        df = df[['Тип варки', 'Объем варки', 'SKU', 'КГ', 'Номер команды', 'Конфигурация варки', 'Вес варки']]
        df.columns = ['boiling_params', 'boiling_volume', 'sku', 'kg', 'packing_team_id', 'configuration', 'total_volume']

        # fill group id
        df['group_id'] = (df['boiling_params'] == '-').astype(int).cumsum() + 1

        # fill total_volume
        df['total_volume'] = np.where((df['sku'] == '-') & (df['total_volume'].isnull()), default_boiling_volume, df['total_volume'])
        df['total_volume'] = df['total_volume'].fillna(method='bfill')

        # fill configuration
        df['configuration'] = np.where((df['sku'] == '-') & (df['configuration'].isnull()), '8000', df['configuration'])
        df['configuration'] = df['configuration'].fillna(method='bfill')

        # remove separators and empty lines
        df = df[df['sku'] != '-']
        df = df[~df['kg'].isnull()]

        # add line name to boiling_params
        df['boiling_params'] = line.name + ',' + df['boiling_params']
        dfs.append(df)

    # update salt group ids
    if len(dfs[0]) >= 1:
        dfs[1]['group_id'] += dfs[0].iloc[-1]['group_id']

    df = pd.concat(dfs).reset_index(drop=True)
    df['sku'] = df['sku'].apply(cast_sku)

    df['boiling'] = df['boiling_params'].apply(cast_boiling)

    # set boiling form factors
    df['ff'] = df['sku'].apply(lambda sku: sku.form_factor)

    # remove Терка from form_factors
    # todo: take from boiling_plan directly!
    df['bff'] = df['ff'].apply(lambda ff: ff if 'Терка' not in ff.name else None)

    # fill Терка empty form factor values
    for idx, grp in df.copy().groupby('group_id'):
        if grp['bff'].isnull().all():
            # todo: hardcode for rubber
            df.loc[grp.index, 'bff'] = cast_form_factor(2)  # Сулугуни "Умалат", 45%, 0,2 кг, т/ф, (9 шт)
        else:
            filled_grp = grp.copy()
            filled_grp = filled_grp.fillna(method='ffill')
            filled_grp = filled_grp.fillna(method='bfill')
            df.loc[grp.index, 'bff'] = filled_grp['bff']

    # validate single boiling
    for idx, grp in df.groupby('group_id'):
        assert len(grp['boiling'].unique()) == 1, "В одной группе варок должен быть только один тип варки."

    # validate kilograms
    for idx, grp in df.groupby('group_id'):
        assert abs(grp['kg'].sum() - grp.iloc[0]['total_volume']) < 1e-5, "Одна из групп варок имеет неверное количество килограмм."

    df = df[['group_id', 'sku', 'kg', 'packing_team_id', 'boiling', 'bff', 'configuration']]

    df = df.reset_index(drop=True)

    if saturate:
        df = saturate_boiling_plan(df)
    return df
