def make_flow_water_boilings(boiling_group_df, first_boiling_id):
    boiling_model = boiling_group_df.iloc[0]["boiling"]
    boiling_volumes, boilings_meltings, packings = BoilingGroupToSchema()(boiling_group_df)
    boilings_dataframes = SchemaToBoilingsDataframes()(boilings_meltings, packings, boiling_model.line.melting_speed)
    boilings = BoilingsDataframesToBoilings()(
        boiling_volumes,
        boilings_dataframes,
        boiling_group_df.iloc[0]["boiling"],
        first_boiling_id,
    )
    return boilings
