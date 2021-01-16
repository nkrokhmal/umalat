from app.schedule_maker.models import *
from app.schedule_maker.calculation import *
from app.enum import LineName

class BoilingGroupToSchema:
    def _calc_boilings_meltings(self, boiling_group_df):
        df = boiling_group_df.copy()
        boiling_model = df.iloc[0]['boiling']

        df['bff_id'] = df['bff'].apply(lambda bff: bff.id)
        df = df.reset_index()

        bff_kgs = df.groupby('bff_id').agg({'kg': 'sum', 'bff': 'first', 'index': 'first'})
        bff_kgs = bff_kgs.sort_values(by='index')

        iterator = SimpleIterator([[row['bff'], row['kg']] for bff_id, row in bff_kgs.iterrows()])

        boiling_volume = 1000 if boiling_model.line.name == LineName.WATER else 850  # todo: make properly
        total_kg = df['kg'].sum()

        assert total_kg % boiling_volume == 0

        boiling_volumes = [boiling_volume] * int(total_kg // boiling_volume)

        res = []
        for boiling_volume in boiling_volumes:
            boiling_meltings = []

            left = boiling_volume

            while left > ERROR:
                bff, left_kg = iterator.current()

                cur_value = min(left, left_kg)

                iterator.current()[-1] -= cur_value
                left -= cur_value

                boiling_meltings.append([bff, cur_value])

                if abs(iterator.current()[-1]) < ERROR:
                    next = iterator.next()
                    if not next and left > ERROR:
                        raise Exception('Could not collect schema')

            res.append(boiling_meltings)
        return res

    def _calc_packings(self, boiling_group_df):
        df = boiling_group_df.copy()

        df['sku_id'] = df['sku'].apply(lambda sku: sku.id)
        df = df.reset_index()

        sku_kgs = df.groupby(['packing_team_id', 'sku_id']).agg({'kg': 'sum', 'sku': 'first', 'bff': 'first', 'index': 'first'})
        sku_kgs = sku_kgs.sort_values(by='index').reset_index()

        res = {}

        for packing_team_id, grp in sku_kgs.groupby('packing_team_id'):
            res[packing_team_id] = []

            for _, row in grp.iterrows():
                res[packing_team_id].append([row['sku'], row['bff'], row['kg']])
        return res

    def __call__(self, boiling_group_df):
        return self._calc_boilings_meltings(boiling_group_df), self._calc_packings(boiling_group_df)


