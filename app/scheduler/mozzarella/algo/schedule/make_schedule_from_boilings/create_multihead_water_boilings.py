from app.imports.runtime import *
from app.scheduler.mozzarella.algo.packing import *
from app.enum import LineName

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]


def create_multihead_water_boilings(left_df: pd.DataFrame):

    # - Init water boilings using multihead

    multihead_water_boilings = [
        row["boiling"]
        for i, row in left_df.iterrows()
        if boiling_has_multihead_packing(row["boiling"])
        and row["boiling"].props["boiling_model"].line.name == LineName.WATER
    ]

    # - Init last multihead boiling

    if multihead_water_boilings:
        last_multihead_water_boiling = multihead_water_boilings[-1]
    else:
        last_multihead_water_boiling = None

    return multihead_water_boilings, last_multihead_water_boiling
