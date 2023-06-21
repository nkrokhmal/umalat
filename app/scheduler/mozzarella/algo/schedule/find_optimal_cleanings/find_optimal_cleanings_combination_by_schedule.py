from app.imports.runtime import *
from app.scheduler.mozzarella.algo.schedule.find_optimal_cleanings.get_distance_between_boilings import (
    get_distance_between_boilings,
)

from app.scheduler.mozzarella.algo.packing import *


from app.scheduler.mozzarella.algo.stats import *


def get_optimal_cleaning_type_by_group_id(schedule):

    # - Get full cleaning duration

    short_cleaning_length = cast_model(Washer, "Короткая мойка термизатора").time

    # - Unfold boilings

    boilings = schedule["master"]["boiling", True]
    boilings = list(sorted(boilings, key=lambda b: b.x[0]))

    # - Get dataframe with all boilings and their properties

    df = pd.DataFrame(
        [
            [
                b1.props["boiling_id"],
                b1["pouring"]["first"]["termizator"].x[0],
                b1["pouring"]["first"]["termizator"].y[0],
                b1.props["boiling_group_df"].iloc[0]["group_id"],
                b1.props["boiling_group_df"].iloc[0]["line"].name,
                get_distance_between_boilings(b1, b2),
            ]
            for b1, b2 in utils.iter_pairs(boilings, method="all")
        ],
        columns=["boiling_id", "x", "y", "group_id", "line_name", "distance"],
    )

    df["conflict_time"] = df["distance"].apply(lambda value: max(short_cleaning_length - value, 0))

    # - Calc is_water_done - has water been finished at this point

    df["is_water_done"] = df["line_name"]
    df["is_water_done"] = np.where(df["is_water_done"] == "Моцарелла в воде", True, np.nan)
    df["is_water_done"] = df["is_water_done"].fillna(method="bfill")
    df["is_water_done"] = df["is_water_done"].shift(-1).fillna(0)
    df["is_water_done"] = df["is_water_done"].astype(bool)
    df["is_water_done"] = ~df["is_water_done"]

    # - Get cleanings

    def _is_cleaning_combination_fit(cleaning_combination):
        # check that distance between boilings without cleaning is less than 15 hours

        separators = [-1] + list(cleaning_combination) + [df.index[-1]]
        for s1, s2 in utils.iter_pairs(separators):
            group = df.loc[s1 + 1 : s2]

            group_length = group.iloc[-1]["y"] - group.iloc[0]["x"]
            if group_length > cast_t("15:00"):
                return False
        return True

    # - Check if no cleanings needed

    if _is_cleaning_combination_fit([]):
        # no cleanings needed, all is good

        return {}

    # - Get available combinations

    available_combination_boiling_nums = []

    for n_cleanings in range(3):
        available_combination_boiling_nums += [
            boiling_nums
            for boiling_nums in itertools.combinations(range(len(df) - 1), n_cleanings)
            if _is_cleaning_combination_fit(boiling_nums)
        ]

    # - Raise if not available combinations found

    if not available_combination_boiling_nums:
        raise Exception("No available combinations found")

    # - Get most optimal cleaning combination

    values1 = [
        [
            boiling_nums,
            sum(df.loc[boiling_num]["conflict_time"] for boiling_num in boiling_nums),
            df.loc[boiling_nums[0]]["is_water_done"],
        ]
        for boiling_nums in available_combination_boiling_nums
    ]

    df1 = pd.DataFrame(values1, columns=["boiling_nums", "total_conflict_time", "is_water_done"])

    # - Take most optimal combination

    df1 = df1.sort_values(by=["total_conflict_time"], ascending=True)
    df1 = df1.sort_values(by=["is_water_done"], ascending=False)

    # take first one
    boiling_nums = df1.iloc[0]["boiling_nums"]

    # - Get output

    cleaning_type_by_group_id = {df.loc[boiling_num]["group_id"]: "short" for boiling_num in boiling_nums}

    # - Return

    return cleaning_type_by_group_id
