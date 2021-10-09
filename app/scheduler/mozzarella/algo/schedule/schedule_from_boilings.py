# fmt: off

from app.imports.runtime import *

from app.scheduler.time import *
from app.scheduler.mozzarella.algo.packing import *
from app.scheduler.shifts import *
from app.enum import LineName

from app.scheduler.mozzarella.algo.schedule.custom_pushers import *
from utils_ak.block_tree import *

STICK_FORM_FACTOR_NAMES = ["Палочки 15.0г", "Палочки 7.5г"]

class Validator(ClassValidator):
    def __init__(self, window=20, strict_order=False, sheet_order=True):
        super().__init__(window=window)
        self.strict_order = strict_order
        self.sheet_order = sheet_order

    def validate__boiling__boiling(self, b1, b2):
        b1s, b2s = min([b1, b2], key=lambda b: b.x[0]), max([b1, b2], key=lambda b: b.x[0])

        # extract boiling models
        boiling_model1 = b1s.props['boiling_model']
        boiling_model2 = b2s.props['boiling_model']
        
        with code('Basic validations'):
            validate_disjoint_by_axis(b1s["pouring"]["first"]["termizator"], b2s["pouring"]["first"]["termizator"])
            validate_disjoint_by_axis(b1s["pouring"]["second"]["pouring_off"], b2s["pouring"]["second"]["pouring_off"])
            validate_disjoint_by_axis(b1s["pouring"]["first"]["pumping_out"], b2s["pouring"]["second"]["pouring_off"])
            validate_disjoint_by_axis(b1s["pouring"]["second"]["pouring_off"], b2s["pouring"]["first"]["pumping_out"])

        with code('Process boilings on the same pouring line'):
            if b1s["pouring"].props["pouring_line"] == b2s["pouring"].props["pouring_line"]:
                # pourings should not intersect, but also five minutes should be between boilings
                validate_disjoint_by_axis(b1s['pouring'], b2s['pouring'], distance=1, ordered=True)

                # if boilings use same drenator - drenator should not intersect with meltings
                if b1s.props["drenator_num"] == b2s.props["drenator_num"]:
                    validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["drenator"])

        # define line names (water/salt) that we work on (which corresponds to the pouring line)
        wln1 = LineName.WATER if b1s["pouring"].props["pouring_line"] in ["0", "1"] else LineName.SALT
        wln2 = LineName.WATER if b2s["pouring"].props["pouring_line"] in ["0", "1"] else LineName.SALT

        if boiling_model1.line.name == boiling_model2.line.name:
            # same lines

            # basic validation
            validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["meltings"])
            for p1, p2 in itertools.product(b1s["melting_and_packing"]["collecting", True], b2s["melting_and_packing"]["collecting", True]):
                validate_disjoint_by_axis(p1, p2)

            # if water and different boilings - cannot intersect serving with meltings
            if boiling_model1.line.name == LineName.WATER and boiling_model1 != boiling_model2:
                # todo later: deprecated, delete
                # validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"])
                if not boiling_model1.is_lactose:
                    _df = b1s.props['boiling_group_df']
                    _df['is_lactose'] = _df['sku'].apply(lambda sku: sku.made_from_boilings[0].is_lactose)
                    if not _df['is_lactose'].any():
                        if boiling_model1.percent == boiling_model2.percent:
                            # 3.3 бл неполная -> 3.3
                            validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"], distance=-4)
                        else:
                            # 3.3 бл неполная -> 3.6
                            validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"], distance=-2)
                    else:
                        # 3.3 бл полная -> 3.3/3.6
                        validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"], distance=-2)
                elif boiling_model1.percent != boiling_model2.percent:
                    # 3.6, 3.3 - add extra 10 minutes
                    validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"], distance=-2)
                else:
                    # 3.3 Альче Белзактозная -> 3.3 Сакко
                    validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"])

            with code('there should be one hour pause between non-"Палочки 15/7" and "Палочки 15/7" form-factors'):
                mp1 = b1s["melting_and_packing"]["melting"]["meltings"]["melting_process", True][-1]
                mp2 = b2s["melting_and_packing"]["melting"]["meltings"]["melting_process", True][0]

                bff1_name = mp1.props["bff"].name
                bff2_name = mp2.props["bff"].name

                sticks = STICK_FORM_FACTOR_NAMES
                if bff1_name not in sticks and bff2_name in sticks:
                    _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
                    _b2s = b2s["melting_and_packing"]["melting"]["meltings"]
                    # at least one hour should pass between meltings
                    validate_disjoint_by_axis(_b1s, _b2s, distance=12, ordered=True)

            with code('there should be one two hour pause between "Палочки 15/7" and non-"Палочки 15/7" form-factors'):
                mp1 = b1s["melting_and_packing"]["melting"]["meltings"]["melting_process", True][-1]
                mp2 = b2s["melting_and_packing"]["melting"]["meltings"]["melting_process", True][0]

                bff1_name = mp1.props["bff"].name
                bff2_name = mp2.props["bff"].name
                sticks = STICK_FORM_FACTOR_NAMES
                if bff1_name in sticks and bff2_name not in sticks:
                    _b1s = b1s["melting_and_packing"]["melting"]['coolings']
                    _b2s = b2s["melting_and_packing"]["melting"]['coolings']
                    # at least one hour should pass between meltings
                    validate_disjoint_by_axis(_b1s, _b2s, distance=24, ordered=True)

            with code('Process lactose switch on salt line'):
                if boiling_model1.line.name == LineName.SALT:
                    if boiling_model1.is_lactose and not boiling_model2.is_lactose:
                        _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
                        _b2s = b2s["melting_and_packing"]["melting"]["serving"]
                        validate_disjoint_by_axis(_b1s, _b2s, distance=2, ordered=True)

                    if not boiling_model1.is_lactose and boiling_model2.is_lactose:
                        _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
                        _b2s = b2s["melting_and_packing"]["melting"]["serving"]
                        validate_disjoint_by_axis(_b1s, _b2s, distance=-2, ordered=True)
        else:
            # different lines

            if wln1 == wln2:
                # same working lines (means that salt and water on the same working line - due to salt switching to the first pouring_line)

                # basic validations
                validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["meltings"])
                validate_disjoint_by_axis(b1s["melting_and_packing"]["melting"]["meltings"], b2s["melting_and_packing"]["melting"]["serving"])

                _b1s = b1s["melting_and_packing"]["melting"]["meltings"]
                _b2s = b2s["melting_and_packing"]["melting"]["meltings"]
                validate_disjoint_by_axis(_b1s, _b2s, distance=7, ordered=True)

        if self.strict_order:
            validate_order_by_axis(b1, b2)

        with code('Order should be strict inside one configuration sheet'):
            if self.sheet_order and b1.props["sheet"] == b2.props["sheet"]:
                validate_order_by_axis(b1, b2)

    @staticmethod
    def validate__boiling__cleaning(b1, b2):
        boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        validate_disjoint_by_axis(boiling["pouring"]["first"]["termizator"], cleaning)

    @staticmethod
    def validate__cleaning__boiling(b1, b2):
        boiling, cleaning = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        validate_disjoint_by_axis(cleaning, boiling["pouring"]["first"]["termizator"])

    @staticmethod
    def validate__boiling__packing_configuration(b1, b2):
        boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        if boiling.props["boiling_model"].line.name != packing_configuration.props["line_name"]:
            return

        for p1 in boiling.iter(
            cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]
        ):
            validate_disjoint_by_axis(p1, b2)

    @staticmethod
    def validate__packing_configuration__boiling(b1, b2):
        boiling, packing_configuration = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
        if boiling.props["boiling_model"].line.name != packing_configuration.props["line_name"]:
            return

        for p1 in boiling.iter(
            cls="collecting", packing_team_id=packing_configuration.props["packing_team_id"]
        ):
            validate_disjoint_by_axis(b1, p1)


def make_termizator_cleaning_block(cleaning_type, **kwargs):
    cleaning_name = 'Короткая мойка термизатора' if cleaning_type == 'short' else 'Длинная мойка термизатора'
    washer = cast_model(Washer, cleaning_name)
    m = BlockMaker(
        "cleaning",
        size=(washer.time // 5, 0),
        cleaning_type=cleaning_type,
        **kwargs,
    )
    return m.root


class ScheduleMaker:
    def _init_block_maker(self):
        self.m = BlockMaker("schedule")
        self.m.root.props.update(date=self.date)
        self.m.block("master")
        self.m.block("extra")
        self.m.block("extra_packings")

        with self.m.block("shifts"):
            self.m.block('cheese_makers')
            self.m.block('water_meltings')
            self.m.block('water_packings')
            self.m.block('salt_meltings')
            self.m.block('salt_packings')

    def _init_lines_df(self):
        # init lines df
        lines_df = pd.DataFrame(
            index=[LineName.WATER, LineName.SALT],
            columns=["iter_props", "start_time", "boilings_left", "latest_boiling"],
        )
        lines_df["latest_boiling"] = None

        # init iter_props
        lines_df.at[LineName.WATER, "iter_props"] = [
            {"pouring_line": str(v1), "drenator_num": str(v2)}
            for v1, v2 in itertools.product([0, 1], [0, 1])
        ]
        lines_df.at[LineName.SALT, "iter_props"] = [
            {"pouring_line": str(v1), "drenator_num": str(v2)}
            for v1, v2 in itertools.product([2, 3], [0, 1])
        ]

        # init start times
        for line_name in [LineName.WATER, LineName.SALT]:
            try:
                lines_df.at[line_name, "start_time"] = cast_time(self.start_times[line_name])
            except:
                raise AssertionError(
                    f"Неверно указано время первой подачи на линии {line_name}"
                )

        # check for missing start time
        if lines_df["start_time"].isnull().any():
            missing_lines = lines_df[lines_df["start_time"].isnull()].index
            raise AssertionError(
                f'Укажите время начала подачи на следующих линиях: {", ".join(missing_lines)}'
            )

        self.lines_df = lines_df

    def _init_left_df(self):

        # make left_df
        values = [
            [
                boiling,
                boiling.props["boiling_model"].line.name,
                boiling.props["sheet"],
            ]
            for boiling in self.boilings
        ]
        left_df = (
            pd.DataFrame(values, columns=["boiling", "line_name", "sheet"])
                .reset_index()
                .sort_values(by=["sheet", "index"])
        )

        self.left_df = left_df

        # check for empty input
        assert len(left_df) > 0, "На вход не подано ни одной варки. Укажите хотя бы одну варку для составления расписания."

    def _init_multihead_water_boilings(self):
        # init water boilings using multihead
        self.multihead_water_boilings = [
            row["boiling"]
            for i, row in self.left_df.iterrows()
            if boiling_has_multihead_packing(row["boiling"])
               and row["boiling"].props["boiling_model"].line.name == LineName.WATER
        ]

        # init last multihead boiling
        if self.multihead_water_boilings:
            self.last_multihead_water_boiling = self.multihead_water_boilings[-1]
        else:
            self.last_multihead_water_boiling = None

    def _process_boiling(self, boiling, shrink_drenators=True, strict_order=False):
        # extract line name
        line_name = boiling.props["boiling_model"].line.name

        # find start_from
        if not self.lines_df.at[line_name, "latest_boiling"]:
            # init
            if self.lines_df.at[line_name, "start_time"]:
                # start time present
                start_from = cast_t(self.lines_df.at[line_name, "start_time"]) - boiling["melting_and_packing"].x[0]
            else:
                # start time not present - start from overall latest boiling from both lines
                latest_boiling = self.lines_df[~self.lines_df["latest_boiling"].isnull()].iloc[0]["latest_boiling"]
                start_from = latest_boiling.x[0]
        else:
            # start from latest boiling
            start_from = self.lines_df.at[line_name, "latest_boiling"].x[0]

        # add configuration if needed
        if self.lines_df.at[line_name, "latest_boiling"]:
            configuration_blocks = make_configuration_blocks(
                self.lines_df.at[line_name, "latest_boiling"],
                boiling,
                self.m,
                line_name,
                between_boilings=True,
            )
            for conf in configuration_blocks:
                conf.props.update(line_name=line_name)
                push(
                    self.m.root["master"],
                    conf,
                    push_func=AxisPusher(start_from="beg"),
                    validator=Validator(),
                )

        # filter iter_props: no two boilings allowed sequentially on the same pouring line
        iter_props = self.lines_df.at[line_name, "iter_props"]
        if self.lines_df.at[line_name, "latest_boiling"]:
            current_pouring_line = self.lines_df.at[line_name, "latest_boiling"].props[
                "pouring_line"
            ]
            iter_props = [
                props
                for props in iter_props
                if props["pouring_line"] != current_pouring_line
            ]

        # push boiling
        push(
            self.m.root["master"],
            boiling,
            push_func=AxisPusher(start_from=start_from),
            iter_props=iter_props,
            validator=Validator(strict_order=strict_order),
            max_tries=100,
        )
        # fix water a little bit: try to push water before - allowing awaiting in line
        if line_name == LineName.WATER and self.lines_df.at[LineName.WATER, "latest_boiling"]:
            boiling.detach_from_parent()
            push(
                self.m.root["master"],
                boiling,
                push_func=AwaitingPusher(max_period=8),
                validator=Validator(strict_order=strict_order),
                max_tries=9,
            )

        if shrink_drenators:
            # fix water a little bit: try to shrink drenator a little bit for compactness
            if self.lines_df.at[LineName.WATER, "latest_boiling"]:
                boiling.detach_from_parent()
                push(
                    self.m.root["master"],
                    boiling,
                    push_func=DrenatorShrinkingPusher(max_period=-2),
                    validator=Validator(strict_order=strict_order),
                    max_tries=3,
                )

        # move rubber packing to extras
        for packing in boiling.iter(cls="packing"):
            if not list(
                    packing.iter(
                        cls="process",
                        sku=lambda sku: "Терка" in sku.form_factor.name,
                    )
            ):
                # rubber not present
                continue

            packing_copy = self.m.copy(packing, with_props=True)
            packing_copy.props.update(extra_props={"start_from": packing.x[0]})
            packing.props.update(deactivated=True) # used in make_configuration_blocks function
            push(self.m.root["extra"], packing_copy, push_func=add_push)

        # add multihead boiling after all water boilings if multihead was present
        if boiling == self.last_multihead_water_boiling:
            push(
                self.m.root["master"],
                self.m.create_block(
                    "multihead_cleaning",
                    x=(boiling.y[0], 0),
                    size=(cast_t("03:00"), 0),
                ),
                push_func=add_push,
            )
            push(
                self.m.root["extra"],
                self.m.create_block(
                    "multihead_cleaning",
                    x=(boiling.y[0], 0),
                    size=(cast_t("03:00"), 0),
                ),
                push_func=add_push,
            )

        # add cleaning after boiling if needed
        cleaning_type = self.cleanings.get(boiling.props["boiling_id"])
        if cleaning_type:
            start_from = boiling["pouring"]["first"]["termizator"].y[0]
            cleaning = make_termizator_cleaning_block(
                cleaning_type,
                x=(boiling["pouring"]["first"]["termizator"].y[0], 0),
                rule='manual',
            )
            push(
                self.m.root["master"],
                cleaning,
                push_func=AxisPusher(start_from=start_from),
                validator=Validator(),
            )

        # set latest boiling
        self.lines_df.at[line_name, "latest_boiling"] = boiling
        return boiling

    def _process_boilings(self, start_configuration, shrink_drenators=True):
        assert len(start_configuration) != 0, "Start configuration not specified"
        # logger.debug('Start configuration', start_configuration=start_configuration)
        cur_boiling_num = 0

        with code('add boilings loop'):
            while True:
                # check if finished
                if len(self.left_df) == 0:
                    break

                # check if only salt left -> start working on 3 line
                if (self.left_df["line_name"] == LineName.SALT).all():
                    self.lines_df.at[LineName.SALT, "iter_props"] = [
                        {"pouring_line": str(v1), "drenator_num": str(v2)}
                        for v1, v2 in itertools.product([2, 3, 1], [0, 1])
                    ]

                next_rows = [grp.iloc[0] for i, grp in self.left_df.groupby('sheet')] # select first rows from each sheet
                cur_lines = len(set([row["line_name"] for row in next_rows]))

                # logger.debug('Current Lines', cur_lines=cur_lines)

                # select next row
                if cur_lines == 1:
                    # one line of sheet left
                    next_row = self.left_df.iloc[0]
                elif cur_lines == 2:
                    # filter rows with latest boiling (any boiling is already present for line)
                    df = self.lines_df[~self.lines_df["latest_boiling"].isnull()]

                    if cur_boiling_num < len(start_configuration):
                        # start from specified configuration
                        line_name = start_configuration[cur_boiling_num]
                        # logger.debug('Chose line by start configuration', line_name=line_name)
                    else:
                        # choose most latest line
                        line_name = (
                            max(df["latest_boiling"], key=lambda b: b.x[0])
                                .props["boiling_model"]
                                .line.name
                        )
                        # reverse
                        line_name = LineName.WATER if line_name == LineName.SALT else LineName.SALT
                        # logger.debug('Chose line by most latest line', line_name=line_name)

                    # select next row -> first for selected line
                    next_row = self.left_df[self.left_df["line_name"] == line_name].iloc[0]
                else:
                    raise Exception("Should not happen")

                # remove newly added row from left rows
                self.left_df = self.left_df[self.left_df["index"] != next_row["index"]]

                if cur_boiling_num < len(start_configuration):
                    # all configuration blocks should start in strict order
                    strict_order = True
                else:
                    strict_order = False

                # insert boiling
                self._process_boiling(next_row["boiling"], shrink_drenators=shrink_drenators, strict_order=strict_order)
                cur_boiling_num += 1

    def _process_extras(self):
        # push extra packings
        class ExtraValidator(ClassValidator):
            def __init__(self):
                super().__init__(window=10)

            @staticmethod
            def validate__packing__packing(b1, b2):
                return validate_disjoint_by_axis(b1, b2)

            @staticmethod
            def validate__multihead_cleaning__packing(b1, b2):
                multihead_cleaning, packing = list(sorted([b1, b2], key=lambda b: b.props["cls"]))
                for process in packing.iter(cls="process"):
                    packer = utils.delistify(process.props['sku'].packers, single=True)
                    if packer.name == 'Мультиголова':
                        validate_disjoint_by_axis(multihead_cleaning, process, distance=1, ordered=True)

        # add multihead to "extra_packings"
        for multihead_cleaning in self.m.root["extra"].iter(cls="multihead_cleaning"):
            push(self.m.root["extra_packings"], multihead_cleaning, push_func=add_push)

        # add packings to "extra_packings"
        for packing in self.m.root["extra"].iter(cls="packing"):
            push(
                self.m.root["extra_packings"],
                packing,
                push_func=AxisPusher(start_from=int(packing.props["extra_props"]["start_from"])),
                validator=ExtraValidator(),
            )

    def _process_cleanings(self):

        with code('Add cleanings if necessary'):
            # extract boilings
            boilings = self.m.root["master"]["boiling", True]
            boilings = list(sorted(boilings, key=lambda b: b.x[0]))

            for a, b in utils.iter_pairs(boilings):
                rest = b["pouring"]["first"]["termizator"].x[0] - a["pouring"]["first"]["termizator"].y[0]

                # extract current cleanings
                cleanings = list(self.m.root["master"].iter(cls="cleaning"))

                # calc in_between and previous cleanings
                in_between_cleanings = [c for c in cleanings if a.x[0] <= c.x[0] <= b.x[0]]
                previous_cleanings = [c for c in cleanings if c.x[0] <= a.x[0]]
                if previous_cleanings:
                    previous_cleaning = max(previous_cleanings, key=lambda c: c.x[0])
                else:
                    previous_cleaning = None

                if not in_between_cleanings:
                    # no current in between cleanings -> try to add if needed

                    # if rest is more than an hour and less than 80 minutes -> short cleaning
                    if 12 <= rest < 18:
                        cleaning = make_termizator_cleaning_block("short", rule='rest_between_60_and_80')
                        cleaning.props.update(x=(a["pouring"]["first"]["termizator"].y[0], 0))
                        push(self.m.root["master"], cleaning, push_func=add_push)

                    # if rest is more than 80 minutes
                    if rest >= 18:
                        if previous_cleaning and a.x[0] - previous_cleaning.x[0] < cast_t("04:00"):
                            # if 4 hours ago or earlier was cleaning -> make short
                            cleaning = make_termizator_cleaning_block("short", rule='rest_after_80_4_hours_cleaning')
                        elif a.x[0] - boilings[0].x[0] < cast_t("04:00"):
                            # if less than 4 hours since day start -> make short
                            cleaning = make_termizator_cleaning_block("short", rule='rest_after_80_4_hours_init')
                        else:
                            # otherwise -> make full
                            cleaning = make_termizator_cleaning_block("full", rule='rest_after_80')
                        cleaning.props.update(x=(a["pouring"]["first"]["termizator"].y[0], 0))
                        push(self.m.root["master"], cleaning, push_func=add_push)

        # add last full cleaning
        last_boiling = max(self.m.root["master"]['boiling', True], key=lambda b: b.y[0])
        start_from = last_boiling["pouring"]["first"]["termizator"].y[0] + 1
        cleaning = make_termizator_cleaning_block("full", rule='closing')  # add five extra minutes
        push(
            self.m.root["master"],
            cleaning,
            push_func=AxisPusher(start_from=start_from),
            validator=Validator(),
        )

    def _process_shifts(self):
        with code('cheese makers'):
            beg = min(self.m.root['master']['boiling', True], key=lambda b: b.x[0]).x[0] - 6  # 0.5h before start
            end = max(self.m.root['master']['boiling', True], key=lambda b: b.y[0])['pouring']['second']['pouring_off'].y[0] + 24  # 2h after last pouring off
            shifts = split_shifts(beg, end)

            for i, (beg, end) in enumerate(shifts, 1):
                push(self.m.root['shifts']['cheese_makers'], push_func=add_push,
                     block=self.m.create_block(
                         "shift",
                         x=(beg, 0),
                         size=(end - beg, 0),
                         shift_num=i
                     ))

        # todo maybe: refactor, code duplication
        with code('Water'):
            water_boilings = [b for b in self.m.root['master']['boiling', True] if b.props['boiling_model'].line.name == LineName.WATER]

            if water_boilings:
                with code('water meltings'):
                    beg = water_boilings[0]['melting_and_packing']['melting'].x[0] - 12  # 1h before start
                    end = water_boilings[-1]['melting_and_packing']['melting'].y[0] + 12  # 1h after end

                    shifts = split_shifts(beg, end)

                    for i, (beg, end) in enumerate(shifts, 1):
                        push(self.m.root['shifts']['water_meltings'], push_func=add_push,
                             block=self.m.create_block(
                                 "shift",
                                 x=(beg, 0),
                                 size=(end - beg, 0),
                                 shift_num=i
                             ))

                with code('water packings'):
                    beg = water_boilings[0]['melting_and_packing']['packing'].x[0] - 18  # 1.5h before start
                    end = water_boilings[-1]['melting_and_packing']['packing'].y[0] + 6  # 0.5h after end

                    shifts = split_shifts(beg, end)

                    for i, (beg, end) in enumerate(shifts, 1):
                        push(self.m.root['shifts']['water_packings'], push_func=add_push,
                             block=self.m.create_block(
                                 "shift",
                                 x=(beg, 0),
                                 size=(end - beg, 0),
                                 shift_num=i
                             ))

        with code('Salt'):
            salt_boilings = [b for b in self.m.root['master']['boiling', True] if b.props['boiling_model'].line.name == LineName.SALT]
            if salt_boilings:
                with code('salt meltings'):
                    beg = salt_boilings[0]['melting_and_packing']['melting'].x[0] - 12  # 1h before start
                    end = salt_boilings[-1]['melting_and_packing']['packing', True][-1].y[0] # end of packing

                    shifts = split_shifts(beg, end)

                    for i, (beg, end) in enumerate(shifts, 1):
                        push(self.m.root['shifts']['salt_meltings'], push_func=add_push,
                             block=self.m.create_block(
                                 "shift",
                                 x=(beg, 0),
                                 size=(end - beg, 0),
                                 shift_num=i
                             ))

                with code('salt packings'):
                    try:
                        beg = salt_boilings[0]['melting_and_packing']['packing', True][0].x[0] - 12  # 1h before start
                        end = salt_boilings[-1]['melting_and_packing']['packing', True][-1].y[0] + 6  # 0.5h after end

                        shifts = split_shifts(beg, end)

                        for i, (beg, end) in enumerate(shifts, 1):
                            push(self.m.root['shifts']['salt_packings'], push_func=add_push,
                                 block=self.m.create_block(
                                     "shift",
                                     x=(beg, 0),
                                     size=(end - beg, 0),
                                     shift_num=i
                                 ))
                    except:
                        pass


    def _fix_first_boiling_of_later_line(self, start_configuration):
        if len(start_configuration) == 1:
            # only one line present - no need for fix
            return

        boilings = list(sorted(self.m.root['master']['boiling', True], key=lambda b: b.x[0]))
        boiling_line_names = [b.props['boiling_model'].line.name for b in boilings]
        # first_boiling_of_later_line_index
        index = boiling_line_names.index(start_configuration[-1])

        if index == len(boilings) - 1:
            # first boiling of later line is last boiling
            return

        b1, b2 = boilings[index], boilings[index + 1]

        with code('Fix packing configuration if needed'):
            boilings_on_line1 = [b for b in boilings if b.props['boiling_model'].line.name == b1.props['boiling_model'].line.name]
            index = boilings_on_line1.index(b1)

            if index != len(boilings_on_line1) - 1:
                # not last boiling
                b3 = boilings_on_line1[index + 1]
                with code('Find packing configuration between b2 and b3'):
                    packing_configurations = [
                        pc
                        for pc in self.m.root["master"]["packing_configuration", True]
                        if pc.x[0] > b1["melting_and_packing"]["collecting", True][0].x[0] # todo maybe: we take first collecting here, but this is not very straightforward
                        and pc.x[0] <= b3["melting_and_packing"]["collecting", True][0].x[0]
                        and pc.props["line_name"] == b1.props["boiling_model"].line.name
                    ]

                    if packing_configurations:
                        pc = utils.delistify(packing_configurations, single=True)
                    else:
                        pc = None

                with code('Push packing configuration further'):
                    if pc:
                        max_push = b3['melting_and_packing']['collecting', True][0].x[0] - pc.x[0]
                        pc.detach_from_parent()
                        push(
                            self.m.root["master"],
                            pc,
                            push_func=BackwardsPusher(max_period=max_push),
                            validator=Validator(window=100, sheet_order=False),
                            max_tries=max_push + 1,
                        )

        # fix boiling
        max_push = b2.x[0] - b1.x[0]
        b1.detach_from_parent()
        push(
            self.m.root["master"],
            b1,
            push_func=BackwardsPusher(max_period=max_push),
            validator=Validator(window=100, sheet_order=False),
            max_tries=max_push + 1,
        )

        # fix order of master blocks
        self.m.root['master'].reorder_children(lambda b: b.x[0])

    def make(self, boilings, date=None, cleanings=None, start_times=None, start_configuration=None, shrink_drenators=True):
        start_configuration = start_configuration or [LineName.SALT]
        self.date = date or datetime.now()
        self.start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
        self.start_times = {k: v if v else None for k, v in start_times.items()}
        self.cleanings = cleanings or {}  # {boiling_id: cleaning}
        self.boilings = boilings

        self._init_block_maker()
        self._init_lines_df()
        self._init_left_df()
        self._init_multihead_water_boilings()
        self._process_boilings(shrink_drenators=shrink_drenators, start_configuration=start_configuration)
        self._process_extras()
        self._fix_first_boiling_of_later_line(start_configuration)
        self._process_cleanings()
        self._process_shifts()
        return self.m.root


def make_schedule_from_boilings(boilings, date=None, cleanings=None, start_times=None, shrink_drenators=True, start_configuration=None):
    return ScheduleMaker().make(boilings, date, cleanings, start_times, shrink_drenators=shrink_drenators, start_configuration=start_configuration)
