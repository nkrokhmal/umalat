# fmt: off
from app.imports.runtime import *

from app.models import *

from app.scheduler.mascarpone.algo.mascarpone_boilings import *
from app.scheduler.mascarpone.algo.cream_cheese_boilings import *
from app.scheduler.mascarpone.algo.cleanings import *

from utils_ak.block_tree import *


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=20)

    @staticmethod
    def validate__mascarpone_boiling_group__mascarpone_boiling_group(b1, b2):
        b1 = b1["boiling", True][-1]
        b2 = b2["boiling", True][0]

        if sum([b1.props.get("is_cream", False), b2.props.get("is_cream", False)]) == 1:
            # one is cream and one is not
            validate_disjoint_by_axis(b1["boiling_process"], b2["boiling_process"])

        assert (
            b1["packing_process"]["packing_group"]["packing", True][-1].y[0] + 2
            <= b2["packing_process"]["packing_group"]["packing", True][0].x[0]
        )
        validate_disjoint_by_axis(
            b1["boiling_process"]["pumping_off"], b2["boiling_process"]["pumping_off"]
        )
        validate_disjoint_by_axis(
            b1["boiling_process"]["pouring"], b2["boiling_process"]["pouring"]
        )

        assert (
            b1["packing_process"]["packing_group"]["P", True][-1].x[0]
            <= b2["boiling_process"]["pumping_off"].x[0]
        )

    @staticmethod
    def validate__mascarpone_boiling_group__cream_cheese_boiling(b1, b2):
        b = b1["boiling", True][-1]
        assert (
            b["packing_process"].y[0] - 1
            <= b2["boiling_process"]["separation", True][0].x[0]
        )


    @staticmethod
    def validate__mascarpone_boiling_group__cleaning(b1, b2):
        if (
            b2.children[0].props["cls"] != "cleaning_sourdough_mascarpone"
            or b1.props["line_nums"] == b2.props["sourdoughs"]
        ):
            for b in b1["boiling", True]:
                validate_disjoint_by_axis(b["boiling_process"], b2)
                assert b["boiling_process"].y[0] + 1 <= b2.x[0]

    @staticmethod
    def validate__cream_cheese_boiling__cream_cheese_boiling(b1, b2):
        assert b1["boiling_process"]["salting", True][-1].y[0] + 1 <= b2["boiling_process"]["separation", True][0].x[0]

    @staticmethod
    def validate__cleaning__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2)
        subclasses = [b.children[0].props["cls"] for b in [b1, b2]]

        a = all("sourdough" not in sub_cls for sub_cls in subclasses)
        b = all("sourdough" in sub_cls for sub_cls in subclasses)

        if a or b:
            assert b1.y[0] + 3 <= b2.x[0]
        else:
            # validate with neighborhood
            validate_disjoint_by_intervals((b1.x[0] - 3, b1.y[0] + 3), (b2.x[0], b2.y[0]))


    @staticmethod
    def validate__cleaning__mascarpone_boiling_group(b1, b2):
        b = b2["boiling", True][0]
        if b1.props["entity"] == "homogenizer":
            assert b1.y[0] + 1 <= b["packing_process"]["N"].x[0]

    @staticmethod
    def validate__cleaning__cream_cheese_boiling(b1, b2):
        if b1.props["entity"] == "homogenizer":
            assert b1.y[0] + 1 <= b2["boiling_process"]["separation", True][0].x[0]

    @staticmethod
    def validate__cream_cheese_boiling__cleaning(b1, b2):
        if b2.props["entity"] == "separator" or (
            (b2.children[0].props["cls"] == "cleaning_sourdough_mascarpone_cream_cheese")
            and len(set(b1.props["sourdoughs"]) & set(b2.props["sourdoughs"])) > 0
        ):
            assert b1["boiling_process"]["separation", True][-1].y[0] + 1 <= b2.x[0]


class BoilingPlanToSchedule:
    def __init__(self):
        self.m = BlockMaker("schedule")

    def _make_mascarpone(self, boiling_plan_df, is_last=False):
        is_cream = boiling_plan_df.iloc[0]["is_cream"]
        boiling_group_dfs = [
            grp for boiling_id, grp in boiling_plan_df.groupby("boiling_id")
        ]
        if not is_cream:
            # create by pairs
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

        for i, bg in enumerate(boiling_groups):
            if is_cream:
                line_nums = [i % 4 + 1]
            else:
                line_nums = [
                    int(boiling_group_df.iloc[0]["sourdough"])
                    for boiling_group_df in bg.props["boiling_group_dfs"]
                ]

            self.m.block(bg,
                 push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                 push_kwargs={'validator': Validator()},
                 # props
                 line_nums=line_nums)

        left_cleaning_lines = list(all_line_nums)
        if not is_cream:
            # clean first sourdoughs asap
            last_groups = []
            for line_nums in all_line_nums:
                cur_groups = [
                    bg for bg in boiling_groups if bg.props["line_nums"] == line_nums
                ]
                if len(cur_groups) == 0:
                    continue
                last_groups.append(cur_groups[-1])
            first_last_group = min(last_groups, key=lambda bg: bg.x[0])

            block = make_cleaning(
                "sourdough_mascarpone",
                sourdoughs=first_last_group.props["line_nums"],
            )

            self.m.block(block,
                    push_func=AxisPusher(start_from="last_beg", start_shift=-30),
                    push_kwargs={'validator': Validator()})
            left_cleaning_lines.remove(first_last_group.props["line_nums"])

            if len(boiling_group_dfs) > 6 or is_last:
                for entity in ["separator", "homogenizer"]:
                    cleaning = make_cleaning(entity)
                    self.m.block(cleaning,
                                 push_func=AxisPusher(start_from="last_beg"),
                                 push_kwargs={'validator': Validator()})

            for line_nums in left_cleaning_lines:
                cleaning = make_cleaning("sourdough_mascarpone", sourdoughs=line_nums)
                self.m.block(cleaning,
                             push_func=AxisPusher(start_from="last_beg", start_shift=-30),
                             push_kwargs={'validator': Validator()})


    def _make_cream_cheese(self, boiling_plan_df):
        boiling_group_dfs = [
            grp for boiling_id, grp in boiling_plan_df.groupby("boiling_id")
        ]

        cream_cheese_blocks = [
            make_cream_cheese_boiling(
                grp,
                sourdoughs=grp.iloc[0]["sourdoughs"],
                boiling_plan_df=boiling_plan_df,
            )
            for i, grp in enumerate(boiling_group_dfs)
        ]

        for block in cream_cheese_blocks:
            self.m.block(block,
                         push_func=AxisPusher(start_from="last_beg", start_shift=-50),
                         push_kwargs={'validator': Validator()})

        # cleanings
        sourdoughs = boiling_plan_df[boiling_plan_df["type"] == "cream_cheese"][
            "sourdoughs"
        ].tolist()
        sourdoughs = utils.remove_duplicates(sourdoughs, key=lambda lst: str(lst))
        sourdoughs = sum(sourdoughs, [])

        for group in utils.crop_to_chunks(sourdoughs, 2):
            block = make_cleaning("sourdough_mascarpone_cream_cheese", sourdoughs=group)
            self.m.block(block,
                         push_func=AxisPusher(start_from="last_beg", start_shift=-30),
                         push_kwargs={'validator': Validator()})

        for entity in ["separator", "homogenizer", "heat_exchanger"]:
            block = make_cleaning(entity)
            self.m.block(block,
                         push_func=AxisPusher(start_from="last_beg"),
                         push_kwargs={'validator': Validator()})

    def __call__(self, boiling_plan_df, first_batch_id=0):
        boiling_plan_df["batch_id"] += first_batch_id - 1
        columns = boiling_plan_df.columns
        boiling_plan_df["tag"] = (
            boiling_plan_df["sku_cls_name"]
            + "-"
            + boiling_plan_df["is_cream"].astype(str)
        )

        df = boiling_plan_df[["tag"] + list(columns)]
        ordered_groups = utils.df_to_ordered_tree(df, recursive=False)
        for i, (group_cls_name, grp) in enumerate(ordered_groups):
            if grp.iloc[0]["type"] == "mascarpone":
                is_last = i == len(ordered_groups) - 1
                self._make_mascarpone(grp, is_last=is_last)
            elif grp.iloc[0]["type"] == "cream_cheese":
                self._make_cream_cheese(grp)
        return self.m.root


def make_schedule(boiling_plan_df, start_batch_id=0):
    return BoilingPlanToSchedule()(boiling_plan_df, start_batch_id)
