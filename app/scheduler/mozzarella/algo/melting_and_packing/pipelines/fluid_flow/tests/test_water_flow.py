import os


os.environ["APP_ENVIRONMENT"] = "interactive"


warnings.filterwarnings("ignore")


def test():
    fn = config.abs_path("app/data/inputs/samples/mozzarella/2021-05-07 План по варкам.xlsx")
    df = read_boiling_plan(fn)
    mark_consecutive_groups(df, "boiling", "boiling_group")
    boiling_group_df = df[df["boiling_group"] == 1]

    for boiling in make_flow_water_boilings(boiling_group_df, first_boiling_id=1):
        print(boiling)


if __name__ == "__main__":
    test()
