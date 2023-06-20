import pandas as pd


def create_left_df(boilings):

    # - Create left df

    values = [
        [
            boiling,
            boiling.props["boiling_model"].line.name,
            boiling.props["sheet"],
        ]
        for boiling in boilings
    ]
    left_df = (
        pd.DataFrame(values, columns=["boiling", "line_name", "sheet"]).reset_index().sort_values(by=["sheet", "index"])
    )

    # - Check for empty input

    assert len(left_df) > 0, "На вход не подано ни одной варки. Укажите хотя бы одну варку для составления расписания."

    # - Return

    return left_df
