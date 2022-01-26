
def update_absolute_batch_id(boiling_plan_df, first_batch_ids):
    boiling_plan_df['absolute_batch_id'] = boiling_plan_df['batch_id']
    for batch_type, grp in boiling_plan_df.groupby('batch_type'):
        boiling_plan_df.loc[grp.index, 'absolute_batch_id'] += first_batch_ids.get(batch_type, 1) - grp['batch_id'].min()
    return boiling_plan_df
