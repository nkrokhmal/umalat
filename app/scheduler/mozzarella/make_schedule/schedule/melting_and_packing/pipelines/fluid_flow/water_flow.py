from app.scheduler.mozzarella.make_schedule.schedule.melting_and_packing.pipelines.fluid_flow.s1_boiling_group_to_schema import (
    BoilingGroupToSchema,
)
from app.scheduler.mozzarella.make_schedule.schedule.melting_and_packing.pipelines.fluid_flow.s2_water_schema_to_boilings_dataframes import (
    SchemaToBoilingsDataframes,
)
from app.scheduler.mozzarella.make_schedule.schedule.melting_and_packing.pipelines.fluid_flow.s3_water_boilings_dataframes_to_boiling import (
    BoilingsDataframesToBoilings,
)


def make_flow_water_boilings(boiling_group_df, first_boiling_id):
    # boiling_model = boiling_group_df.iloc[0]["boiling"]
    melting_speed = boiling_group_df.iloc[0].melting_speed
    boiling_volumes, boilings_meltings, packings = BoilingGroupToSchema()(boiling_group_df)
    boilings_dataframes = SchemaToBoilingsDataframes()(boilings_meltings, packings, melting_speed)
    boilings = BoilingsDataframesToBoilings()(
        boiling_volumes,
        boilings_dataframes,
        boiling_group_df.iloc[0]["boiling"],
        first_boiling_id,
    )
    return boilings
