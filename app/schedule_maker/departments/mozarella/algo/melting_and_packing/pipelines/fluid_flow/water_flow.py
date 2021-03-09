from app.schedule_maker.departments.mozarella.algo.melting_and_packing.pipelines.fluid_flow import (
    BoilingGroupToSchema,
)
from app.schedule_maker.departments.mozarella.algo.melting_and_packing.pipelines.fluid_flow import (
    SchemaToBoilingsDataframes,
)
from app.schedule_maker.departments.mozarella.algo.melting_and_packing.pipelines.fluid_flow import (
    BoilingsDataframesToBoilings,
)


def make_flow_water_boilings(boiling_group_df, start_from_id):
    boiling_model = boiling_group_df.iloc[0]["boiling"]
    boiling_volumes, boilings_meltings, packings = BoilingGroupToSchema()(
        boiling_group_df
    )
    boilings_dataframes = SchemaToBoilingsDataframes()(
        boilings_meltings, packings, boiling_model.line.melting_speed
    )
    boilings = BoilingsDataframesToBoilings()(
        boiling_volumes,
        boilings_dataframes,
        boiling_group_df.iloc[0]["boiling"],
        start_from_id,
    )
    return boilings
