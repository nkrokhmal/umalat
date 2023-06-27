# DEPRECATED 2023-06-21

# import os
#
# from app.scheduler.mozzarella.algo.melting_and_packing import make_flow_water_boilings
# from app.scheduler.mozzarella.boiling_plan import read_boiling_plan
# from utils_ak.pandas import mark_consecutive_groups
#
# os.environ["APP_ENVIRONMENT"] = "interactive"
#
#
# from app.scheduler.mozzarella import *
# import warnings
# warnings.filterwarnings("ignore")
#
#
# def test():
#     fn = config.abs_path(
#         "app/data/inputs/samples/mozzarella/2021-05-07 План по варкам.xlsx"
#     )
#     df = read_boiling_plan(fn)
#     mark_consecutive_groups(df, "boiling", "boiling_group")
#     boiling_group_df = df[df["boiling_group"] == 1]
#
#     for boiling in make_flow_water_boilings(boiling_group_df, first_boiling_id=1):
#         print(boiling)
#
#
# if __name__ == "__main__":
#     test()
