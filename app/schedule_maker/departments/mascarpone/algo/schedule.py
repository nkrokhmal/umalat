from utils_ak.block_tree import *

from app.schedule_maker.models import *

from app.schedule_maker.departments.mascarpone.algo.mascarpone_boilings import *
from app.schedule_maker.departments.mascarpone.algo.cream_cheese_boilings import *
from app.schedule_maker.departments.mascarpone.algo.cleanings import *

validator = ClassValidator(window=20)


def validate(b1, b2):
    b1 = listify(b1["boiling"])[-1]
    b2 = listify(b2["boiling"])[0]

    assert (
        b1["packing_process"]["packing"].y[0] + 2
        <= b2["packing_process"]["packing"].x[0]
    )
    validate_disjoint_by_axis(
        b1["boiling_process"]["pumping_off"], b2["boiling_process"]["pumping_off"]
    )


validator.add("mascarpone_boiling_group", "mascarpone_boiling_group", validate)


def validate(b1, b2):
    b = listify(b1["boiling"])[-1]
    assert (
        b["packing_process"].y[0] - 1
        <= listify(b2["boiling_process"]["separation"])[0].x[0]
    )


validator.add("mascarpone_boiling_group", "cream_cheese_boiling", validate)


def validate(b1, b2):
    if (
        b2.children[0].props["cls"] != "cleaning_sourdough_mascarpone"
        or b1.props["line_nums"] == b2.props["sourdough_nums"]
    ):
        for b in listify(b1["boiling"]):
            validate_disjoint_by_axis(b["boiling_process"], b2)
            assert b["boiling_process"].y[0] + 1 <= b2.x[0]


validator.add("mascarpone_boiling_group", "cleaning", validate)


def validate(b1, b2):
    assert listify(b1["boiling_process"]["salting"][-1].y[0]) <= listify(
        b2["boiling_process"]["separation"][0].y[0]
    )


validator.add("cream_cheese_boiling", "cream_cheese_boiling", validate)


def validate(b1, b2):
    validate_disjoint_by_axis(b1, b2)
    subclasses = [b.children[0].props["cls"] for b in [b1, b2]]

    a = all("sourdough" not in sub_cls for sub_cls in subclasses)
    b = all("sourdough" in sub_cls for sub_cls in subclasses)

    if a or b:
        assert b1.y[0] + 3 <= b2.x[0]
    else:
        # validate with neighborhood
        validate_disjoint_by_intervals((b1.x[0] - 3, b1.y[0] + 3), (b2.x[0], b2.y[0]))


validator.add("cleaning", "cleaning", validate)


def validate(b1, b2):
    b = listify(b2["boiling"])[0]
    if b1.props["entity"] == "homogenizer":
        assert b1.y[0] + 1 <= b["packing_process"]["N"].x[0]


validator.add("cleaning", "mascarpone_boiling_group", validate)


def validate(b1, b2):
    if b1.props["entity"] == "separator":
        assert b1.y[0] + 1 <= listify(b2["boiling_process"]["separation"])[0].x[0]

    if b1.props["entity"] == "homogenizer":
        assert b1.y[0] + 1 <= listify(b2["boiling_process"]["salting"])[0].x[0]


validator.add("cleaning", "cream_cheese_boiling", validate)


def validate(b1, b2):
    if b2.props["entity"] == "separator" or (
        (b2.children[0].props["cls"] == "cleaning_sourdough_mascarpone_cream_cheese")
        and (b1.props["sourdough_num"] in b2.props["sourdough_nums"])
    ):
        assert listify(b1["boiling_process"]["separation"])[-1].y[0] + 1 <= b2.x[0]


validator.add("cream_cheese_boiling", "cleaning", validate)


class BoilingPlanToSchedule:
    def __init__(self):
        self.maker, self.make = init_block_maker("schedule")

    def _make_mascarpone(self, boiling_plan_df, is_last=False):
        is_cream = boiling_plan_df.iloc[0]["is_cream"]
        boiling_group_dfs = [
            grp for boiling_id, grp in boiling_plan_df.groupby("boiling_id")
        ]
        if not is_cream:
            assert len(boiling_group_dfs) % 2 == 0

            boiling_groups = []

            for i in range(len(boiling_group_dfs) // 2):
                boiling_groups.append(
                    make_mascarpone_boiling_group(boiling_group_dfs[i * 2 : i * 2 + 2])
                )
        else:
            boiling_groups = []
            for boiling_group_df in boiling_group_dfs:
                boiling_groups.append(make_mascarpone_boiling_group([boiling_group_df]))

        all_line_nums = [[1, 2], [3, 4]]

        boiling_volumes = [800, 600]
        for i, bg in enumerate(boiling_groups):

            line_nums = [
                int(boiling_group_df.iloc[0]["sourdough"])
                for boiling_group_df in bg.props["boiling_group_dfs"]
            ]
            bg.props.update(line_nums=line_nums, boiling_volume=boiling_volumes[i % 2])
            push(
                self.maker.root,
                bg,
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                validator=validator,
            )

        if not is_cream:
            # cleanings
            if len(boiling_group_dfs) > 6 or is_last:
                for entity in ["separator", "homogenizer"]:
                    block = make_cleaning(entity)
                    push(
                        self.maker.root,
                        block,
                        push_func=AxisPusher(start_from="last_beg"),
                        validator=validator,
                    )

            for line_nums in all_line_nums:
                block = make_cleaning("sourdough_mascarpone", sourdough_nums=line_nums)
                push(
                    self.maker.root,
                    block,
                    push_func=AxisPusher(start_from="last_beg", start_shift=-30),
                    validator=validator,
                )

    def _make_cream_cheese(self, boiling_plan_df):
        boiling_group_dfs = [
            grp for boiling_id, grp in boiling_plan_df.groupby("boiling_id")
        ]
        cream_cheese_blocks = [
            make_cream_cheese_boiling(
                grp, sourdough_num=i % 3 + 4, boiling_plan_df=boiling_plan_df
            )
            for i, grp in enumerate(boiling_group_dfs)
        ]

        for block in cream_cheese_blocks:
            push(
                self.maker.root,
                block,
                push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                validator=validator,
            )

        # cleanings
        if len(cream_cheese_blocks) == 1:
            groups = [[4]]
        elif len(cream_cheese_blocks) == 2:
            groups = [[4, 5]]
        else:
            # >= 3
            groups = [[4, 5], [6]]

        for group in groups:
            block = make_cleaning(
                "sourdough_mascarpone_cream_cheese", sourdough_nums=group
            )
            push(
                self.maker.root,
                block,
                push_func=AxisPusher(start_from="last_beg", start_shift=-30),
                validator=validator,
            )

        for entity in ["separator", "homogenizer", "heat_exchanger"]:
            block = make_cleaning(entity)
            push(
                self.maker.root,
                block,
                push_func=AxisPusher(start_from="last_beg"),
                validator=validator,
            )

    def __call__(self, boiling_plan_df):
        columns = boiling_plan_df.columns
        boiling_plan_df["sku_cls_name"] = boiling_plan_df["sku"].apply(
            lambda sku: str(sku.__class__)
        )
        boiling_plan_df["tag"] = (
            boiling_plan_df["sku_cls_name"]
            + "-"
            + boiling_plan_df["is_cream"].astype(str)
        )

        df = boiling_plan_df[["tag"] + list(columns)]
        ordered_groups = df_to_ordered_tree(df, recursive=False)
        for i, (group_cls_name, grp) in enumerate(ordered_groups):
            if "Mascarpone" in group_cls_name:
                is_last = i == len(ordered_groups) - 1
                self._make_mascarpone(grp, is_last=is_last)
            elif "CreamCheese" in group_cls_name:
                self._make_cream_cheese(grp)
        return self.maker.root


def make_schedule(boiling_plan_df):
    return BoilingPlanToSchedule()(boiling_plan_df)
