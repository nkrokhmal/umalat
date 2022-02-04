from app.imports.runtime import *
from app.scheduler.time import *
from app.scheduler.parsing_new import *

COLUMN_SHIFT = 5 # header 4 + 1 for one-indexing

def parse_schedule(ws_obj):
    df = utils.read_merged_cells_df(ws_obj, basic_features=False)

    with code('Find time'):
        # find time index rows
        time_index_rows = df[df['label'].astype(str).str.contains('График')]['x1'].unique()
        row = time_index_rows[0]

        start_time = cast_time_from_hour_label(df[(df["x0"] == 5) & (df["x1"] == row)].iloc[0]["label"])


    with code('find rows'):
        df1 = df[df['x0'] >= 5]  # column header out

        # find cheese_maker_rows
        rows = []
        for row_num in df1['x1'].unique():
            row_labels = [str(row['label']) for i, row in df1[df1['x1'] == row_num].iterrows()]
            row_labels = [re.sub(r'\s+', ' ', label) for label in row_labels if label]

            with code('find all headers'):
                _labels = [label.replace('налив', '') for label in row_labels]
                _labels = [re.sub(r'\s+', '', label) for label in _labels]
                int_labels = [int(label) for label in _labels if utils.is_int_like(label)]

                if not ('05' in row_labels and '55' in row_labels):
                    # not a time header
                    if int_labels:
                        rows.append(row_num)

    # leave only bath lines (3 items)
    rows = [rows[0], rows[2], rows[4]]

    parsed_schedule = {'baths': []}
    for i, row in enumerate(rows):
        with code('find line blocks'):
            def _filter_func(group):
                try:
                    return utils.is_int_like(group.iloc[0]["label"].split(" ")[0])
                except:
                    return False

            def _split_func(prev_row, row):
                try:
                    return utils.is_int_like(row["label"].split(" ")[0])
                except:
                    return False

            line_blocks = parse_line(df, row, split_criteria=basic_criteria(split_func=_split_func))
            line_blocks = [line_block for line_block in line_blocks if _filter_func(line_block)]

        with code('expand blocks'):
            def expand_block(df, df_block):
                return df[(df['x1'].isin([df_block['x1'].min(), df_block['x1'].min() + 1])) &
                          (df_block['x0'].min() <= df['x0']) &
                          (df['x0'] < df_block['y0'].max())]

            baths_df = [expand_block(df, line_block) for line_block in line_blocks]

        with code('Convert boilings to dictionaries'):
            for boiling_df in baths_df:
                boiling_df['label'] = np.where(boiling_df['label'].isnull() | (boiling_df['label'] == ''), boiling_df['color'], boiling_df['label'])
                boiling = boiling_df.set_index('label').to_dict(orient='index')
                boiling = {'blocks': {k: [v['x0'] + cast_t(start_time) - COLUMN_SHIFT, v['y0'] + cast_t(start_time) - COLUMN_SHIFT] for k, v in boiling.items()}}

                boiling['boiling_id'] = int(boiling_df.iloc[0]["label"].split(" ")[0])
                boiling['interval'] = [boiling_df['x0'].min() + cast_t(start_time) - COLUMN_SHIFT, boiling_df['y0'].max() + cast_t(start_time) - COLUMN_SHIFT]
                boiling['interval_time'] = list(map(cast_time, boiling['interval']))
                boiling['line'] = i + 1

                parsed_schedule['baths'].append(boiling)

    # calc boilings
    df = pd.DataFrame(parsed_schedule['baths'])

    parsed_schedule['boilings'] = []
    for boiling_id, grp in df.groupby('boiling_id'):
        boiling = {'boiling_id': boiling_id}
        boiling['interval'] = [min(grp['interval'].apply(lambda interval: interval[0])), max(grp['interval'].apply(lambda interval: interval[1]))]
        boiling['interval_time'] = list(map(cast_human_time, boiling['interval']))
        parsed_schedule['boilings'].append(boiling)
    return parsed_schedule


def test():
    fn = os.path.join(basedir, 'app/data/static/samples/outputs/by_department/ricotta/Расписание рикотта 2.xlsx')
    df = pd.DataFrame(parse_schedule((fn, 'Расписание'))['boilings'])[['boiling_id', 'interval_time']]
    print(df)


if __name__ == '__main__':
    test()