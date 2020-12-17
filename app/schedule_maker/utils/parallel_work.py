from utils_ak import remove_duplicates
import pandas as pd

def get_total_parallel_time(input_speed, df):
    t = 0

    # start with slow ones
    df = df.sort_values(by='speed')

    while df['qty'].sum() > 0:
        speed_left = input_speed

        groups = remove_duplicates(df['group'])
        group_df = pd.DataFrame([False] * len(groups), index=groups, columns=['used'])

        df['cur_speed'] = 0

        for group in groups:
            grp = df[df['group'] == group]

            # set cur speed
            for i, row in grp.iterrows():
                if row['qty'] == 0:
                    continue

                if group_df.at[row['group'], 'used']:
                    break

                df.at[i, 'cur_speed'] = min(speed_left, row['speed'])
                speed_left -= df.at[i, 'cur_speed']

                group_df.at[row['group'], 'used'] = True

        df['time_left'] = df['qty'] / df['cur_speed']
        min_time_left = df['time_left'][df['time_left'] > 0].min()
        t += min_time_left
        df['qty'] -= df['cur_speed'] * min_time_left
    return t


if __name__ == '__main__':
    # one group element can be used at one time

    df = pd.DataFrame(columns=['speed', 'qty'])
    df['qty'] = [800, 50]
    df['speed'] = [728, 360]
    df['group'] = ['non-rubber', 'rubber']

    print(get_total_parallel_time(1020, df))