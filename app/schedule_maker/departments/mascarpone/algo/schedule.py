from utils_ak.block_tree import *

from app.schedule_maker.models import *

from app.schedule_maker.departments.mascarpone.algo.mascarpone_boilings import *
from app.schedule_maker.departments.mascarpone.algo.cream_cheese_boilings import *
from app.schedule_maker.departments.mascarpone.algo.cleanings import *

validator = ClassValidator(window=3)


def validate(b1, b2):
    b1 = listify(b1["boiling"])[-1]
    b2 = listify(b2["boiling"])[0]

    assert (
        b1["packing_process"]["packing"].y[0] + 2
        <= b2["packing_process"]["packing"].x[0]
    )
    validate_disjoint_by_axis(
        b1["boiling_process"]["separation"], b2["boiling_process"]["separation"]
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
    assert b1.y[0] + 3 <= b2.x[0]


validator.add("cleaning", "cleaning", validate)


def validate(b1, b2):
    b = listify(b2["boiling"])[0]
    if b1.props["entity"] == "homogenizer":
        assert b1.y[0] + 1 <= b["packing_process"]["N"].x[0]


validator.add("cleaning", "mascarpone_boiling_group", validate)


class BoilingPlanToSchedule:
    def __init__(self):
        self.maker, self.make = init_block_maker("schedule")

    def _make_mascarpone(self, boiling_plan_df):
        boiling_group_dfs = [
            grp for boiling_id, grp in boiling_plan_df.groupby("boiling_id")
        ]
        assert len(boiling_group_dfs) % 2 == 0

        boiling_groups = []

        for i in range(len(boiling_group_dfs) // 2):
            b1, b2 = boiling_group_dfs[i * 2], boiling_group_dfs[i * 2 + 1]
            boiling_groups.append(make_mascarpone_boiling_group(b1, b2))

        all_line_nums = [[0, 1], [2, 3]]
        for i, bg in enumerate(boiling_groups):
            line_nums = all_line_nums[i % 2]
            bg.props.update(line_nums=line_nums)
            push(
                self.maker.root,
                bg,
                push_func=AxisPusher(start_from=0),
                validator=validator,
            )

        # cleanings
        for entity in ["separator", "homogenizer", "heat_exchanger"]:
            block = make_cleaning(entity)
            push(
                self.maker.root,
                block,
                push_func=AxisPusher(start_from="last_beg"),
                validator=validator,
            )

    def _make_cream_cheese(self, boiling_plan_df):
        boiling_group_dfs = [
            grp for boiling_id, grp in boiling_plan_df.groupby("boiling_id")
        ]
        cream_cheese_blocks = [
            make_cream_cheese_boiling(grp) for grp in boiling_group_dfs
        ]

        for block in cream_cheese_blocks:
            push(
                self.maker.root,
                block,
                push_func=AxisPusher(start_from=0),
                validator=validator,
            )

    def __call__(self, boiling_plan_df):
        columns = boiling_plan_df.columns
        boiling_plan_df["sku_cls_name"] = boiling_plan_df["sku"].apply(
            lambda sku: str(sku.__class__)
        )

        df = boiling_plan_df[["sku_cls_name"] + list(columns)]

        for group_cls_name, grp in df_to_ordered_tree(df, recursive=False):
            if "Mascarpone" in group_cls_name:
                self._make_mascarpone(grp)
            # elif "CreamCheese" in group_cls_name:
            #     self._make_cream_cheese(grp)
            #     break
        return self.maker.root


def make_schedule(boiling_plan_df):
    return BoilingPlanToSchedule()(boiling_plan_df)
