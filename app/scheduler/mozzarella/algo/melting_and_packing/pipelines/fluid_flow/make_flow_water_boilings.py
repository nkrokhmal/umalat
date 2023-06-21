import copy

import pandas as pd

from app.scheduler.mozzarella.algo.melting_and_packing.pipelines.fluid_flow.s1_boiling_group_to_schema import (
    BoilingGroupToSchema,
)
from app.scheduler.mozzarella.algo.melting_and_packing.pipelines.fluid_flow.s2_water_schema_to_boilings_dataframes import (
    SchemaToBoilingsDataframes,
)
from app.scheduler.mozzarella.algo.melting_and_packing.pipelines.fluid_flow.s3_water_boilings_dataframes_to_boiling import (
    BoilingsDataframesToBoilings,
)

CACHE_BOILING_GROUP_DF_TO_BOILINGS_AND_FIRST_BOILING_ID = {}


def make_flow_water_boilings(boiling_group_df, first_boiling_id):

    # - Calc hash of boiling_group_df

    hash_df = boiling_group_df[["sku_name", "original_kg"]]
    hash_ = hash_df.to_json()

    # - Generate boilings if needed

    if hash_ not in CACHE_BOILING_GROUP_DF_TO_BOILINGS_AND_FIRST_BOILING_ID:
        boiling_model = boiling_group_df.iloc[0]["boiling"]
        boiling_volumes, boilings_meltings, packings = BoilingGroupToSchema()(boiling_group_df)
        boilings_dataframes = SchemaToBoilingsDataframes()(
            boilings_meltings, packings, boiling_model.line.melting_speed
        )
        boilings = BoilingsDataframesToBoilings()(
            boiling_volumes,
            boilings_dataframes,
            boiling_group_df.iloc[0]["boiling"],
            first_boiling_id,
        )

        CACHE_BOILING_GROUP_DF_TO_BOILINGS_AND_FIRST_BOILING_ID[hash_] = (boilings, first_boiling_id)

    # - Get boilings

    boilings, cached_first_boiling_id = CACHE_BOILING_GROUP_DF_TO_BOILINGS_AND_FIRST_BOILING_ID[hash_]

    # - Copy boilings

    boilings = [copy.deepcopy(boiling) for boiling in boilings]

    # - Set proper boiling_id

    for boiling in boilings:
        boiling.props.update(boiling_id=boiling.props["boiling_id"] + first_boiling_id - cached_first_boiling_id)

    return boilings
