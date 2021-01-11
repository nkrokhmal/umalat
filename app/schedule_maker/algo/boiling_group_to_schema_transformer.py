from app.schedule_maker.models import *

ERROR = 1e-5

# todo: make properly
def cast_bff(sku):
    if sku == cast_sku(4):
        return cast_boiling_form_factor(5)
    elif sku == cast_sku(37):
        return cast_boiling_form_factor(8)
    else:
        return sku.boiling_form_factors[0]


class BoilingGroupToSchemaTransformer:
    def _calc_melting_speed(self, boiling_group_df):
        boiling_type = boiling_group_df.iloc[0]['boiling'].boiling_type
        return 900 if boiling_type == 'water' else 1020  # todo: make properly

    def _calc_boilings_meltings(self, boiling_group_df):
        df = boiling_group_df.copy()

        # todo: take from boiling_plan
        df['bff'] = df['sku'].apply(cast_bff)
        df['bff_id'] = df['bff'].apply(lambda bff: bff.id)
        df = df.reset_index()

        bff_kgs = df.groupby('bff_id').agg({'kg': 'sum', 'bff': 'first', 'index': 'first'})
        bff_kgs = bff_kgs.sort_values(by='index')

        iterator = SimpleBoundedIterator([[row['bff'], row['kg']] for bff_id, row in bff_kgs.iterrows()])

        boiling_type = df.iloc[0]['boiling'].boiling_type
        boiling_volume = 1000 if boiling_type == 'water' else 850  # todo: make properly
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
                    iterator.next()

            res.append(boiling_meltings)
        return res

    def _calc_packings(self, boiling_group_df):
        df = boiling_group_df.copy()

        # todo: take from boiling_plan
        df['bff'] = df['sku'].apply(cast_bff)

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
        return self._calc_boilings_meltings(boiling_group_df), self._calc_packings(boiling_group_df), self._calc_melting_speed(boiling_group_df)


