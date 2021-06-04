# todo archived: deprecated
# from app.imports.runtime import *
# from app.models import *
# from app.enum import LineName
#
#
# class RandomBoilingPlanGenerator:
#     def _gen_random_boiling_plan(self, group_id, line_name):
#         boilings = db.session.query(Boiling).all()
#         boilings = [boiling for boiling in boilings if boiling.line.name == line_name]
#         boiling = random.choice(boilings)
#         skus = db.session.query(SKU).all()
#         skus = [sku for sku in skus if sku.packing_speed]
#         skus = [sku for sku in skus if boiling in sku.made_from_boilings]
#
#         values = []
#
#         default_boiling_volume = cast_model(Line, line_name).output_ton
#
#         left = default_boiling_volume
#
#         while left > ERROR:
#             sku = random.choice(skus)
#
#             if random.randint(0, 1) == 0:
#                 kg = left
#             else:
#                 kg = random.randint(1, left)
#
#             if random.randint(0, 10) != 0:
#                 packing_team_id = 1
#             else:
#                 packing_team_id = 2
#
#             if sku.form_factor and sku.form_factor.default_cooling_technology:
#                 bff = sku.form_factor
#             else:
#                 # rubber
#                 bff = cast_form_factor(2)
#
#             configuration = "8000"
#
#             values.append(
#                 [group_id, sku, boiling, kg, packing_team_id, bff, configuration]
#             )
#
#             left -= kg
#
#         return pd.DataFrame(
#             values,
#             columns=[
#                 "group_id",
#                 "sku",
#                 "boiling",
#                 "kg",
#                 "packing_team_id",
#                 "bff",
#                 "configuration",
#             ],
#         )
#
#     def __call__(self, *args, **kwargs):
#         dfs = []
#
#         cur_batch_id = 0
#         for _ in range(random.randint(0, 20)):
#             dfs.append(self._gen_random_boiling_plan(cur_batch_id, LineName.WATER))
#             cur_batch_id += 1
#         for _ in range(random.randint(0, 20)):
#             dfs.append(self._gen_random_boiling_plan(cur_batch_id, LineName.SALT))
#             cur_batch_id += 1
#         return pd.concat(dfs).reset_index(drop=True)
#
#
# class BoilingPlanDfSerializer:
#     def write(self, df, fn):
#         df = df.copy()
#         df["sku"] = df["sku"].apply(lambda sku: sku.id)
#         df["boiling"] = df["boiling"].apply(lambda boiling: boiling.id)
#         df["bff"] = df["bff"].apply(lambda bff: bff.id)
#         df.to_csv(fn, index=False)
#
#     def read(self, fn):
#         df = pd.read_csv(fn)
#         df["sku"] = df["sku"].apply(cast_sku)
#         df["boiling"] = df["boiling"].apply(cast_boiling)
#         df["bff"] = df["bff"].apply(cast_form_factor)
#         return df
