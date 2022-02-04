from app.imports.runtime import *
from utils_ak.block_tree import *
from app.scheduler.parsing_new.group_intervals import *


def parse_line(merged_cells_df, line_row, split_criteria):
    df1 = merged_cells_df[merged_cells_df["x1"] == line_row]  # filter column header
    groups = group_intervals(
        [row for i, row in df1.iterrows()],
        interval_func=lambda row: [row["x0"], row["y0"]],
        split_criteria=split_criteria
    )

    groups = [pd.DataFrame(group) for group in groups]
    return groups



def test1():
    def expand_block(df, df_block):
        return df[(df['x1'].isin([df_block['x1'].min(), df_block['x1'].min() + 1])) &
                  (df_block['x0'].min() <= df['x0']) &
                  (df['x0'] < df_block['y0'].max())]

    fn = os.path.join(basedir, 'app/data/tests/parsing/2.xlsx')
    merged_cells_df = utils.read_merged_cells_df((fn, 'Sheet1'), basic_features=False)
    print(merged_cells_df)
    groups = parse_line(merged_cells_df, 3, split_criteria=basic_criteria(max_length=2))
    df_block = expand_block(merged_cells_df, groups[0])
    print(df_block)


if __name__ == '__main__':
    test1()