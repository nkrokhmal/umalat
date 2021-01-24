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

    df = pd.concat(dfs).reset_index(drop=True)
    df['sku'] = df['sku'].apply(cast_sku)

    df['boiling'] = df['boiling_params'].apply(cast_boiling)

    # set boiling form factors
    df['ff'] = df['sku'].apply(lambda sku: sku.form_factor)

    # remove Терка from form_factors
    df['bff'] = df['ff'].apply(lambda ff: ff if ff.name != 'Терка' else None)

    # fill Терка empty form factor values
    for idx, grp in df.copy().groupby('batch_id'):
        if grp['bff'].isnull().all():
            # todo: hardcode for rubber
            df.loc[grp.index, 'bff'] = cast_form_factor(2) # Сулугуни "Умалат", 45%, 0,2 кг, т/ф, (9 шт)
        else:
            filled_grp = grp.copy()
            filled_grp = filled_grp.fillna(method='ffill')
            filled_grp = filled_grp.fillna(method='bfill')
            df.loc[grp.index, 'bff'] = filled_grp['bff']

    # validate single boiling
    for idx, grp in df.groupby('batch_id'):
        assert len(grp['boiling'].unique()) == 1, "В одной объединенной группе варок должен быть только один тип варки."

    # validate kilograms
    for idx, grp in df.groupby('batch_id'):
        boiling_model = grp.iloc[0]['boiling']
        assert grp['kg'].sum() % boiling_model.line.output_ton == 0, "Одна из варок имеет неверное количество килограмм."
    df = df[['batch_id', 'sku', 'kg', 'packing_team_id', 'boiling', 'bff']]

    return df.reset_index(drop=True)


class RandomBoilingPlanGenerator:
    def _gen_random_boiling_plan(self, batch_id, line_name):
        boilings = db.session.query(Boiling).all()
        boilings = [boiling for boiling in boilings if boiling.line.name == line_name]
        boiling = random.choice(boilings)
        skus = db.session.query(SKU).all()
        skus = [sku for sku in skus if sku.packing_speed]
        skus = [sku for sku in skus if boiling in sku.made_from_boilings]

        values = []

        boiling_volume = 1000 if line_name == LineName.WATER else 850

        left = boiling_volume

        while left > ERROR:
            sku = random.choice(skus)

            if random.randint(0, 1) == 0:
                kg = left
            else:
                kg = random.randint(1, left)

            if random.randint(0, 10) != 0:
                packing_team_id = 1
            else:
                packing_team_id = 2

            if sku.form_factor and sku.form_factor.default_cooling_technology:
                bff = sku.form_factor
            else:
                # rubber
                bff = cast_form_factor(2)

            values.append([batch_id, sku, boiling, kg, packing_team_id, bff])

            left -= kg
        return pd.DataFrame(values, columns=['batch_id', 'sku', 'boiling', 'kg', 'packing_team_id', 'bff'])

    def __call__(self, *args, **kwargs):
        dfs = []

        cur_batch_id = 0
        for _ in range(random.randint(0, 20)):
            dfs.append(self._gen_random_boiling_plan(cur_batch_id, LineName.WATER))
            cur_batch_id += 1
        for _ in range(random.randint(0, 20)):
            dfs.append(self._gen_random_boiling_plan(cur_batch_id, LineName.SALT))
            cur_batch_id += 1
        return pd.concat(dfs).reset_index(drop=True)


class BoilingPlanDfSerializer:
    def write(self, df, fn):
        df = df.copy()
        df['sku'] = df['sku'].apply(lambda sku: sku.id)
        df['boiling'] = df['boiling'].apply(lambda boiling: boiling.id)
        df['bff'] = df['bff'].apply(lambda bff: bff.id)
        df.to_csv(fn, index=False)

    def read(self, fn):
        df = pd.read_csv(fn)
        df['sku'] = df['sku'].apply(cast_sku)
        df['boiling'] = df['boiling'].apply(cast_boiling)
        df['bff'] = df['bff'].apply(cast_form_factor)
        return df
