import pandas as pd


def parse_schedule_basic_info(schedule):
    schedule_json = schedule.to_dict(
        props=[
            {"key": "x", "value": lambda b: list(b.props["x"])},
            {"key": "size", "value": lambda b: list(b.props["size"])},
            {"key": "cleaning_type", "cls": "cleaning"},
            {
                "key": "boiling_group_df",
                "cls": "boiling",
            },
        ]
    )
    boilings_json = [x for x in schedule_json["children"][0]["children"] if x["cls"] == "boiling"]
    boilings_json = list(sorted(boilings_json, key=lambda b_json: b_json["props"]["x"][0]))

    dfs = []
    for b_json in boilings_json:
        dfs.append(b_json["props"]["boiling_group_df"])

    res = pd.concat(dfs)
    res["sheet"] = 0
    return res
