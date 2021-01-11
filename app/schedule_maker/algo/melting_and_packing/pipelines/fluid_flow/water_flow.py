from app.schedule_maker.algo.melting_and_packing.pipelines.fluid_flow.s1_boiling_group_to_schema import boiling_group_to_schema
from app.schedule_maker.algo.melting_and_packing.pipelines.fluid_flow.s2_water_schema_to_boilings_dataframes import schema_to_boilings_dataframes
from app.schedule_maker.algo.melting_and_packing.pipelines.fluid_flow.s3_water_boilings_dataframes_to_boiling import boilings_dataframes_to_boilings


def make_flow_water_boilings(boiling_group_df, start_from_id):
    boilings_meltings, packings, melting_speed = boiling_group_to_schema()(boiling_group_df)
    boilings_dataframes = schema_to_boilings_dataframes()(boilings_meltings, packings, melting_speed)
    boilings = boilings_dataframes_to_boilings()(boilings_dataframes, boiling_group_df.iloc[0]['boiling'], start_from_id)
    return boilings