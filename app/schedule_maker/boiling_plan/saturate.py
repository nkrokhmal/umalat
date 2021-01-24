def saturate_boiling_plan(boiling_plan_df):
    df = boiling_plan_df.copy()
    df['line'] = df['boiling'].apply(lambda boiling_model: boiling_model.line)

    # fill boiling volumes
    values = []
    for i, row in df.iterrows():
        values.append([float(x.strip()) * row['line'].output_per_ton / 8000 for x in row['configuration'].split(',')])
    df['boiling_volumes'] = values

    return df