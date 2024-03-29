from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.block_tree.validation import ClassValidator, validate_disjoint_by_axis
from utils_ak.builtin.collection import crop_to_chunks, remove_duplicates
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.pandas.pandas_tools import df_to_ordered_tree

from app.scheduler.archive.mascarpone.algo.cleanings import make_cleaning
from app.scheduler.archive.mascarpone.algo.mascarpone_boilings import make_mascarpone_boiling_group
from app.scheduler.split_shifts_utils import split_shifts_by_time
from app.scheduler.time_utils import cast_t


class Validator(ClassValidator):
    def __init__(self):
        super().__init__(window=20)

    @staticmethod
    def validate__mascarpone_boiling_group__mascarpone_boiling_group(b1, b2):
        b1 = b1["boiling", True][-1]
        b2 = b2["boiling", True][0]

        if b1.props["sourdough"] == b2.props["sourdough"]:
            validate_disjoint_by_axis(b1["boiling_process"], b2["boiling_process"], ordered=True)

        if sum([b1.props.get("is_cream", False), b2.props.get("is_cream", False)]) == 1:
            # one is cream and one is not
            validate_disjoint_by_axis(b1["boiling_process"], b2["boiling_process"])

        _b1 = b1["packing_process"]["packing_group"]["packing", True][-1]
        _b2 = b2["packing_process"]["packing_group"]["packing", True][0]
        validate_disjoint_by_axis(_b1, _b2, distance=2, ordered=True)
        validate_disjoint_by_axis(b1["boiling_process"]["pumping_off"], b2["boiling_process"]["pumping_off"])
        validate_disjoint_by_axis(b1["boiling_process"]["pouring"], b2["boiling_process"]["pouring"])

        _b1 = b1["packing_process"]["packing_group"]["P", True][-1]
        _b2 = b2["boiling_process"]["pumping_off"]
        assert _b1.x[0] <= _b2.x[0]

    @staticmethod
    def validate__mascarpone_boiling_group__cream_cheese_boiling(b1, b2):
        _b1 = b1["boiling", True][-1]
        _b2 = b2["boiling_process"]["separation", True][0]
        validate_disjoint_by_axis(_b1, _b2, distance=-1, ordered=True)

    @staticmethod
    def validate__preparation__mascarpone_boiling_group(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__preparation__cream_cheese_boiling(b1, b2):
        validate_disjoint_by_axis(b1, b2, ordered=True)

    @staticmethod
    def validate__mascarpone_boiling_group__cleaning(b1, b2):
        if (
            b2.children[0].props["cls"] != "cleaning_sourdough_mascarpone"
            or b1.props["line_nums"] == b2.props["sourdoughs"]
        ):
            for b in b1["boiling", True]:
                validate_disjoint_by_axis(b["boiling_process"], b2, distance=1, ordered=True)

    @staticmethod
    def validate__cream_cheese_boiling__cream_cheese_boiling(b1, b2):
        _b1 = b1["boiling_process"]["salting", True][-1]
        _b2 = b2["boiling_process"]["separation", True][0]
        validate_disjoint_by_axis(_b1, _b2, distance=1, ordered=True)

    @staticmethod
    def validate__cleaning__cleaning(b1, b2):
        validate_disjoint_by_axis(b1, b2)
        subclasses = [b.children[0].props["cls"] for b in [b1, b2]]

        a = all("sourdough" not in sub_cls for sub_cls in subclasses)
        b = all("sourdough" in sub_cls for sub_cls in subclasses)

        if a or b:
            validate_disjoint_by_axis(b1, b2, distance=3, ordered=True)
        else:
            validate_disjoint_by_axis(b1, b2, distance=3, ordered=False)

    @staticmethod
    def validate__cleaning__mascarpone_boiling_group(b1, b2):
        b = b2["boiling", True][0]
        if b1.props["entity"] == "homogenizer":
            validate_disjoint_by_axis(b1, b["packing_process"]["N"], distance=1, ordered=True)

    @staticmethod
    def validate__cleaning__cream_cheese_boiling(b1, b2):
        if b1.props["entity"] == "homogenizer":
            validate_disjoint_by_axis(b1, b2["boiling_process"]["separation", True][0], distance=1, ordered=True)

    @staticmethod
    def validate__cream_cheese_boiling__cleaning(b1, b2):
        if b2.props["entity"] == "separator" or (
            (b2.children[0].props["cls"] == "cleaning_sourdough_mascarpone_cream_cheese")
            and len(set(b1.props["sourdoughs"]) & set(b2.props["sourdoughs"])) > 0
        ):
            _b1 = b1["boiling_process"]["separation", True][-1]
            _b2 = b2
            validate_disjoint_by_axis(_b1, b2, distance=1, ordered=True)


class BoilingPlanToSchedule:
    def __init__(self):
        self.m = BlockMaker("schedule")

    def _make_preparation(self):
        self.m.block("preparation", size=(6, 0))

    def _make_mascarpone(self, boiling_plan_df, is_last=False):
        is_cream = boiling_plan_df.iloc[0]["is_cream"]
        batch_dfs = [grp for batch_id, grp in boiling_plan_df.groupby("absolute_batch_id")]
        if not is_cream:
            boiling_groups = []

            for batch_df in batch_dfs:
                boiling_group_dfs = [grp for boiling_id, grp in batch_df.groupby("boiling_id")]
                boiling_groups.append(make_mascarpone_boiling_group(boiling_group_dfs))
        else:
            # cream
            boiling_groups = []
            for batch_df in batch_dfs:
                boiling_groups.append(make_mascarpone_boiling_group([batch_df]))

        all_line_nums = [[1, 2], [3, 4]]

        for i, bg in enumerate(boiling_groups):
            if is_cream:
                line_nums = [i % 4 + 1]
            else:
                line_nums = [
                    int(boiling_group_df.iloc[0]["sourdough"]) for boiling_group_df in bg.props["boiling_group_dfs"]
                ]

            # set sourdough for each boiling
            for i, boiling in enumerate(bg["boiling", True]):
                boiling.props.update(sourdough=line_nums[i])

            self.m.block(
                bg,
                push_func=AxisPusher(start_from="max_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
                # props
                line_nums=line_nums,
            )

        def _is_on_line_num(line_nums, compared_line_nums):
            if compared_line_nums == line_nums:
                return True

            if len(line_nums) == 1:
                return line_nums[0] in compared_line_nums

            return False

        left_cleaning_lines = list(all_line_nums)
        if not is_cream:
            # clean first sourdoughs asap
            last_groups = []
            for line_nums in all_line_nums:
                cur_groups = [bg for bg in boiling_groups if _is_on_line_num(bg.props["line_nums"], line_nums)]
                if len(cur_groups) == 0:
                    continue
                last_groups.append(cur_groups[-1])

            first_last_group = min(last_groups, key=lambda bg: bg.x[0])

            block = make_cleaning(
                "sourdough_mascarpone",
                sourdoughs=first_last_group.props["line_nums"],
            )

            self.m.block(
                block,
                push_func=AxisPusher(start_from="max_beg", start_shift=-30),
                push_kwargs={"validator": Validator()},
            )
            left_cleaning_lines.remove(
                [x for x in left_cleaning_lines if _is_on_line_num(first_last_group.props["line_nums"], x)][0]
            )

            if len(boiling_plan_df.groupby("boiling_id")) > 6 or is_last:
                for entity in ["separator", "homogenizer"]:
                    cleaning = make_cleaning(entity)
                    self.m.block(
                        cleaning, push_func=AxisPusher(start_from="max_beg"), push_kwargs={"validator": Validator()}
                    )

            for line_nums in left_cleaning_lines:
                cleaning = make_cleaning("sourdough_mascarpone", sourdoughs=line_nums)
                self.m.block(
                    cleaning,
                    push_func=AxisPusher(start_from="max_beg", start_shift=-30),
                    push_kwargs={"validator": Validator()},
                )

    def _make_cream_cheese(self, boiling_plan_df):
        boiling_group_dfs = [grp for boiling_id, grp in boiling_plan_df.groupby("boiling_id")]

        cream_cheese_blocks = [
            make_cream_cheese_boiling(
                grp,
                sourdoughs=grp.iloc[0]["sourdoughs"],
                boiling_plan_df=boiling_plan_df,
            )
            for i, grp in enumerate(boiling_group_dfs)
        ]

        for block in cream_cheese_blocks:
            self.m.block(
                block,
                push_func=AxisPusher(start_from="max_beg", start_shift=-50),
                push_kwargs={"validator": Validator()},
            )

        # cleanings
        sourdoughs = boiling_plan_df[boiling_plan_df["type"] == "cream_cheese"]["sourdoughs"].tolist()
        sourdoughs = remove_duplicates(sourdoughs, key=lambda lst: str(lst))
        sourdoughs = sum(sourdoughs, [])

        for group in crop_to_chunks(sourdoughs, 2):
            block = make_cleaning("sourdough_mascarpone_cream_cheese", sourdoughs=group)
            self.m.block(
                block,
                push_func=AxisPusher(start_from="max_beg", start_shift=-30),
                push_kwargs={"validator": Validator()},
            )

        for entity in ["separator", "homogenizer", "heat_exchanger"]:
            block = make_cleaning(entity)
            self.m.block(block, push_func=AxisPusher(start_from="max_beg"), push_kwargs={"validator": Validator()})

    def _make_shifts(self, start_time):
        with self.m.block("shifts", x=(0, 0), push_func=add_push):
            self.m.block("meltings")
            self.m.block("packings")

        with code("meltings"):
            beg = self.m.root.x[0]
            end = self.m.root.y[0]

            with code("Calc shift time properly"):
                shift_t = cast_t("18:00")
                if shift_t <= beg + cast_t(start_time):
                    # add day
                    shift_t += cast_t("00:00+1")

            shifts = split_shifts_by_time(beg + cast_t(start_time), end + cast_t(start_time), shift_t, min_shift=12)

            # fix start time
            shifts = [[beg - cast_t(start_time), end - cast_t(start_time)] for beg, end in shifts]

            for i, (beg, end) in enumerate(shifts, 1):
                push(
                    self.m.root["shifts"]["meltings"],
                    push_func=add_push,
                    block=self.m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
                )

        with code("packings"):
            packings = self.m.root.find(cls="packing")
            beg = packings[0].x[0] - 12  # 1h before
            end = packings[-1].y[0] + 12  # 1h after

            with code("Calc shift time properly"):
                shift_t = cast_t("18:00")
                if shift_t <= beg + cast_t(start_time):
                    # add day
                    shift_t += cast_t("00:00+1")

            shifts = split_shifts_by_time(beg + cast_t(start_time), end + cast_t(start_time), shift_t, min_shift=12)
            # fix start time
            shifts = [[beg - cast_t(start_time), end - cast_t(start_time)] for beg, end in shifts]

            for i, (beg, end) in enumerate(shifts, 1):
                push(
                    self.m.root["shifts"]["packings"],
                    push_func=add_push,
                    block=self.m.create_block("shift", x=(beg, 0), size=(end - beg, 0), shift_num=i),
                )

    def _make_boilings(self, boiling_plan_df):
        columns = boiling_plan_df.columns

        boiling_plan_df["tag"] = boiling_plan_df["sku_cls_name"] + "-" + boiling_plan_df["is_cream"].astype(str)
        df = boiling_plan_df[["tag"] + list(columns)]
        ordered_groups = df_to_ordered_tree(df, recursive=False)
        for i, (group_cls_name, grp) in enumerate(ordered_groups):
            if grp.iloc[0]["type"] == "mascarpone":
                is_last = i == len(ordered_groups) - 1
                self._make_mascarpone(grp, is_last=is_last)
            elif grp.iloc[0]["type"] == "cream_cheese":
                self._make_cream_cheese(grp)

    def __call__(self, boiling_plan_df, start_time="07:00"):
        self._make_preparation()
        self._make_boilings(boiling_plan_df)
        self._make_shifts(start_time)
        self.m.root.props.update(x=(cast_t(start_time), 0))
        return self.m.root


def make_schedule(boiling_plan_df, start_time="07:00"):
    return BoilingPlanToSchedule()(boiling_plan_df, start_time=start_time)
