import typing as tp

from dataclasses import dataclass
from pathlib import Path

import openpyxl.worksheet.worksheet
import pandas as pd

from utils_ak.openpyxl.openpyxl_tools import (  # todo next: fix import [@marklidenberg, #kolya]
    read_merged_and_colored_cells_df,
    read_merged_cells_df,
)

from app.imports.runtime import *
from app.main import main
from app.scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@main.route("/download_mozzarella_schedule", methods=["GET"])
@flask_login.login_required
def download_mozzarella_schedule():
    date = flask.request.args.get("date")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["SCHEDULE_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, path=f"{date} Расписание моцарелла.xlsx", as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_mozzarella_boiling_plan", methods=["GET"])
@flask_login.login_required
def download_mozzarella_boiling_plan():
    date = flask.request.args.get("date")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        flask.current_app.config["BOILING_PLAN_FOLDER"],
    )
    response = flask.send_from_directory(
        directory=uploads, path=f"{date} План по варкам моцарелла.xlsx", as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_last_packer_plan", methods=["GET"])
def download_last_packer_plan():
    date = flask.request.args.get("date", None)

    if date is None:
        last_schedule_path = max(
            glob.glob(
                f"{os.path.dirname(flask.current_app.root_path)}/{flask.current_app.config['DYNAMIC_DIR']}/*/"
                f"approved/*Расписание моцарелла*"
            )
        )
    else:
        last_schedule_paths = glob.glob(
            f"{os.path.dirname(flask.current_app.root_path)}/{flask.current_app.config['DYNAMIC_DIR']}/{date}/"
            f"approved/*Расписание моцарелла*"
        )
        if not last_schedule_paths:
            raise PackerParserException(f"Нет файла расписания моцареллы за дату {date}")
        last_schedule_path = last_schedule_paths[0]

    wb = openpyxl.load_workbook(filename=last_schedule_path, data_only=True)

    try:
        boiling_plan_df = to_boiling_plan(wb)
    except Exception as e:
        logger.warning(f"Schedule file hasn't saved properly {e}")
        wb.save(last_schedule_path)
        wb = openpyxl.load_workbook(filename=last_schedule_path, data_only=True)
        boiling_plan_df = to_boiling_plan(wb, validate=False)

    parser = PackerParser(wb["Расписание"], boiling_plan_df)
    dfs_water = list(parser.parse_water())
    dfs_salt = list(parser.parse_salt())

    result_df = pd.concat(dfs_water + dfs_salt)
    result_df["speed"] = result_df["sku"].apply(lambda x: x.packing_speed)
    result_df = result_df[["sku_name", "code", "packer", "speed", "total_time", "pause", "original_kg", "batch_id"]]
    result_df.rename({"original_kg": "kg"}, axis=1, inplace=True)
    result_df["sku_name"] = result_df["sku_name"].apply(lambda x: x.replace(";", ","))
    result_df["packer"] = result_df["packer"].apply(lambda x: x.replace(";", ","))

    result_path = Path(last_schedule_path).parent / "packers.csv"
    result_df.to_csv(result_path, sep=";")
    response = flask.send_from_directory(directory=result_path.parent, path="packers.csv", as_attachment=True)
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@dataclass
class ScheduleParams:
    reconfiguration_color: str = "#ff0000"
    packer_color: str = "#f2dcdb"

    water_packer_x: tuple[int] | None = None
    salt_packers_x: tuple[int, int] | None = None


class PackerParserException(Exception):
    ...


class PackerParser:
    def __init__(self, ws: openpyxl.worksheet.worksheet.Worksheet, boiling_plan_df: pd.DataFrame) -> None:
        self.df = read_merged_and_colored_cells_df(ws, basic_features=False)
        self.boiling_plan_df = boiling_plan_df
        self.boiling_plan_df["sku_name"] = self.boiling_plan_df["sku"].apply(lambda x: x.name)
        self.params = ScheduleParams()
        self.update_schedule_params()

    def update_schedule_params(self) -> None:
        water_df = self.df[self.df["label"] == "Линия плавления моцареллы в воде №1"]["x1"]
        if water_df.empty:
            self.params.water_packer_x = None
        else:
            x1 = water_df.iloc[0]
            self.params.water_packer_x = (
                self.df[(self.df["x1"] > x1) & (self.df["label"] == "Смена 1")]["x1"].min() + 3,
            )

        salt_df = self.df[self.df["label"] == "Линия плавления моцареллы в рассоле №2"]["x1"]
        if salt_df.empty:
            self.params.salt_packers_x = None
        else:
            x1 = salt_df.iloc[0]
            salt_x = self.df[(self.df["x1"] > x1) & (self.df["label"] == "Смена 1")]["x1"].min() + 3
            self.params.salt_packers_x = (salt_x, salt_x + 3)

    def parse_packings(self, line="water"):
        x_coordinates = self.params.water_packer_x if line == "water" else self.params.salt_packers_x
        packing_info = {}
        extra_change_dfs = []
        for x in x_coordinates[::-1]:
            batch_df = self.df[self.df["x1"] == x - 2]
            batch_df["is_int"] = batch_df.label.apply(is_int)

            extra_change_df = batch_df[batch_df.label == "замена воды "]
            extra_change_df["diff"] = extra_change_df["y0"] - extra_change_df["x0"]
            extra_change_dfs.append(extra_change_df)

            packing_df = self.df[(self.df["x1"] == x) & (self.df["color"] == self.params.packer_color)]
            reconfig_df = self.df[(self.df["x1"] == x) & (self.df["color"] == self.params.reconfiguration_color)]

            for _, row in batch_df[batch_df["is_int"]].iterrows():
                if row["y0"] - row["x0"] != 3:
                    continue

                descr_df = batch_df[batch_df["x0"] == row["y0"]]
                if descr_df.empty:
                    raise PackerParserException(f"Не удается считать варку с номером {row['label']}")

                beg, end = row["x0"], descr_df.iloc[0]["y0"]
                boiling_packing_df = packing_df[(packing_df["x0"] >= beg) & (packing_df["x0"] <= end)]

                packings = []
                for _, p_row in boiling_packing_df.iterrows():
                    p_beg, p_end = p_row["x0"], p_row["y0"]
                    if not reconfig_df[reconfig_df["y0"] == p_beg].empty:
                        p_beg -= 1
                    packings.append(
                        {
                            "beg": p_beg,
                            "end": p_end,
                            "line": x,
                        }
                    )

                batch_id = int(row["label"])
                if batch_id in packing_info:
                    packing_info[batch_id]["beg"] = min(packing_info[batch_id]["beg"], beg)
                    packing_info[batch_id]["packings"] += packings
                    packing_info[batch_id]["lines"].append(x)

                else:
                    packing_info[batch_id] = {"beg": beg, "end": end, "lines": [x], "packings": packings}
        return packing_info, pd.concat(extra_change_dfs)

    # def filter_packer(self, packer_x: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    #     packing_df = self.df[(self.df["x1"] == packer_x) & (self.df["color"] == self.params.packer_color)]
    #     reconfig_df = self.df[(self.df["x1"] == packer_x) & (self.df["color"] == self.params.reconfiguration_color)]
    #     return packing_df, reconfig_df

    @staticmethod
    def group_boiling_sku(df) -> pd.DataFrame:
        tmp = df.copy()
        tmp["order_id"] = tmp.index
        return (
            tmp.groupby(["group_id", "sku_name"])
            .agg({"original_kg": "sum", "sku": "first", "order_id": "first"})
            .sort_values(by="order_id")
            .reset_index()
        )

    def match_boiling_and_packer(
        self, boiling_df: pd.DataFrame, packer_info: dict, extra_change_df: pd.DataFrame, line_name: str
    ) -> pd.DataFrame:
        result = []
        group_ids = sorted(boiling_df.group_id.unique())
        if len(packer_info) != len(group_ids):
            raise PackerParserException(f"Число варок  на линии {line_name} не совпадает с расписанием")

        for key, group_id in zip(sorted(packer_info.keys()), group_ids):
            info = packer_info[key]
            df = boiling_df[boiling_df.group_id == group_id]
            if len(info["packings"]) != len(df):
                raise PackerParserException(
                    f"Количество sku в варке {key} на линии {line_name} не совпадает с расписанием"
                )

            for i, value in enumerate(info["packings"]):
                result.append(
                    {
                        "beg": value["beg"],
                        "end": value["end"],
                        "batch_id": key,
                        "total_time": (value["end"] - value["beg"]) * 5,
                        "sku": df["sku"].iloc[i],
                        "original_kg": df["original_kg"].iloc[i],
                        "pause": 0,
                    }
                )

        df = pd.DataFrame(result).sort_values(by="beg")
        if not df.empty:
            df["pause"] = (df["beg"] - df["end"].shift(1)).fillna(0)
            df["pause"] = 5 * df["pause"]
            df.loc[df["pause"] < 0, "pause"] = 0
            df["sku_name"] = df["sku"].apply(lambda x: x.name)
            df["code"] = df["sku"].apply(lambda x: x.code)
            df["packer"] = df["sku"].apply(lambda x: x.packers[0].name)

        for i, row in df.iterrows():
            if i == 0:
                continue
            if row["pause"] == 0:
                continue
            df.loc[i, "pause"] -= (
                extra_change_df[
                    (extra_change_df["y0"] <= row["beg"]) & (extra_change_df["x0"] >= df.iloc[i - 1]["end"])
                ]["diff"].sum()
                * 5
            )

        self.distribute_pause(df)
        return df

    @staticmethod
    def distribute_pause(df: pd.DataFrame):
        for _, df_batch in df.groupby("batch_id"):
            idx = []
            for i, (row_id, row) in enumerate(df_batch[::-1].iterrows()):
                if i == len(df_batch) - 1:
                    break
                idx.append(row_id)
                if row["pause"] != 0:
                    sum_kg = df.loc[idx]["original_kg"].sum()
                    df.loc[idx, "pause"] = row["pause"] * df["original_kg"] / sum_kg
                    idx = []

        df["pause"] = np.round(df["pause"], 2)
        return df

    def parse_water(self) -> tp.Generator[pd.DataFrame, None, None]:
        if self.params.water_packer_x is None:
            yield pd.DataFrame()
            return

        water_df = self.boiling_plan_df[self.boiling_plan_df["line"].apply(lambda x: x.name == LineName.WATER)]
        water_df = self.group_boiling_sku(water_df)
        packing_info, extra_change_df = self.parse_packings("water")

        yield self.match_boiling_and_packer(water_df, packing_info, extra_change_df, "Вода")

    def parse_salt(self) -> tp.Generator[pd.DataFrame, None, None]:
        if self.params.salt_packers_x is None:
            yield pd.DataFrame()
            return

        salt_df = self.boiling_plan_df[self.boiling_plan_df["line"].apply(lambda x: x.name == LineName.SALT)]
        salt_df = self.group_boiling_sku(salt_df)
        packing_info, extra_change_df = self.parse_packings("salt")

        yield self.match_boiling_and_packer(salt_df, packing_info, extra_change_df, "Соль")
