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


@main.route("/download_last_packer_plan", methods=["GET", "POST"])
def download_last_packer_plan():
    last_schedule_path = max(
        glob.glob(
            f"{os.path.dirname(flask.current_app.root_path)}/{flask.current_app.config['DYNAMIC_DIR']}/*/"
            f"approved/*Расписание моцарелла*"
        )
    )

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
    result_df = result_df[["sku_name", "code", "packer", "speed", "total_time", "pause", "kg"]]
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

    water_packer_x: int = None
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
            self.params.water_packer_x = self.df[(self.df["x1"] > x1) & (self.df["label"] == "Смена 1")]["x1"].min() + 3

        salt_df = self.df[self.df["label"] == "Линия плавления моцареллы в рассоле №2"]["x1"]
        if salt_df.empty:
            self.params.salt_packers_x = None
        else:
            x1 = salt_df.iloc[0]
            salt_x = self.df[(self.df["x1"] > x1) & (self.df["label"] == "Смена 1")]["x1"].min() + 3
            self.params.salt_packers_x = (salt_x, salt_x + 3)

    def filter_packer(self, packer_x: int) -> tuple[pd.DataFrame, pd.DataFrame]:
        packing_df = self.df[(self.df["x1"] == packer_x) & (self.df["color"] == self.params.packer_color)]
        reconfig_df = self.df[(self.df["x1"] == packer_x) & (self.df["color"] == self.params.reconfiguration_color)]
        return packing_df, reconfig_df

    @staticmethod
    def group_boiling_sku(df) -> pd.DataFrame:
        tmp = df.copy()
        tmp["order_id"] = tmp.index
        return (
            tmp.groupby(["group_id", "sku_name"])
            .agg({"kg": "sum", "sku": "first", "order_id": "first"})
            .sort_values(by="order_id")
            .reset_index()
        )

    @staticmethod
    def match_boiling_and_packer(
        boiling_df: pd.DataFrame, packer_df: pd.DataFrame, reconfiguration_df: pd.DataFrame, line_name: str
    ) -> pd.DataFrame:
        result = []
        if len(packer_df) > len(boiling_df):
            raise PackerParserException(f"Число различных SKU на линии {line_name} в варках не совпадает с расписанием")

        boiling_df = boiling_df.drop(boiling_df.nsmallest(len(boiling_df) - len(packer_df), columns=["kg"]).index)
        for i, (_, row) in enumerate(packer_df.iterrows()):
            beg, end = row["x0"], row["y0"]
            if not reconfiguration_df[reconfiguration_df["y0"] == beg].empty:
                beg -= 1
            result.append(
                {
                    "beg": beg,
                    "end": end,
                    "total_time": (end - beg) * 5,
                    "sku": boiling_df["sku"].iloc[i],
                    "kg": boiling_df["kg"].iloc[i],
                    "pause": 0,
                }
            )
        df = pd.DataFrame(result)
        if not df.empty:
            df["pause"] = (df["beg"] - df["end"].shift(1)).fillna(0)
            df["pause"] = 5 * df["pause"]
            df["sku_name"] = df["sku"].apply(lambda x: x.name)
            df["code"] = df["sku"].apply(lambda x: x.code)
            df["packer"] = df["sku"].apply(lambda x: x.packers[0].name)
        return df

    def parse_water(self) -> tp.Generator[pd.DataFrame, None, None]:
        if self.params.water_packer_x is None:
            yield pd.DataFrame()
            return

        water_df = self.boiling_plan_df[self.boiling_plan_df["line"].apply(lambda x: x.name == LineName.WATER)]
        packing_df, reconfig_df = self.filter_packer(self.params.water_packer_x)

        water_df = self.group_boiling_sku(water_df)
        yield self.match_boiling_and_packer(water_df, packing_df, reconfig_df, "Вода")

    def parse_salt(self) -> tp.Generator[pd.DataFrame, None, None]:
        if self.params.salt_packers_x is None:
            yield pd.DataFrame()
            return

        salt_df = self.boiling_plan_df[self.boiling_plan_df["line"].apply(lambda x: x.name == LineName.SALT)]
        for i, x in enumerate(self.params.salt_packers_x):
            packing_df, reconfig_df = self.filter_packer(x)
            if i == 0:
                line_name = "Соль"
                salt_df_filter = salt_df[salt_df["sku"].apply(lambda x: "Терка" not in x.form_factor.name)]
            else:
                line_name = "Соль, терка"
                salt_df_filter = salt_df[salt_df["sku"].apply(lambda x: "Терка" in x.form_factor.name)]

            salt_df_filter = self.group_boiling_sku(salt_df_filter)

            yield self.match_boiling_and_packer(salt_df_filter, packing_df, reconfig_df, line_name)
