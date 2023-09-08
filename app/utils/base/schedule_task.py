from typing import Generic, Type, TypeVar

import flask
import pandas as pd

from app.imports.runtime import *
from app.utils.features.draw_utils import *
from app.utils.files.utils import create_dir


ModelType = TypeVar("ModelType")


class BaseScheduleTask(Generic[ModelType]):
    def __init__(self, df, date, model: Type[ModelType], department, df_packing=None):
        self.df = df
        self.date = date
        self.df_packing = df_packing
        self.model = model
        self.department = department

        self.update_df()

    def update_df(self):
        if "sku_name" not in self.df.columns:
            self.df["sku_name"] = self.df["sku"].apply(lambda x: x.name)

        if "original_kg" not in self.df.columns:
            if "kg" not in self.df.columns:
                raise Exception("No column with kg in dataframe")
            else:
                self.df["original_kg"] = self.df["kg"]

        # if "line" in self.df.columns:
        #     self.df["line"] = self.df["line"].apply(lambda x: x.name)

    def update_boiling_schedule_task(self):
        logger.debug("update_boiling_schedule_task")
        data_dir = create_dir(
            self.date.strftime(flask.current_app.config["DATE_FORMAT"]), flask.current_app.config["TASK_FOLDER"]
        )
        path = os.path.join(data_dir, f"{self.date.date()} {self.department}.csv")
        columns = ["batch", "sku", "code", "in_box", "kg", "boxes_count", "start", "finish"]
        if not os.path.exists(path):
            df_task = pd.DataFrame(columns=columns)
            df_task.to_csv(path, index=False, sep=";")

        df_task = pd.read_csv(path, sep=";")
        df_task.drop(df_task.index, inplace=True)

        for batch_id, grp in self.df.groupby("absolute_batch_id"):
            for i, row in grp.iterrows():
                if row["sku"].group.name != "Качокавалло":
                    kg = round(row["original_kg"])
                    boxes_count = math.ceil(row["original_kg"] / row["sku"].in_box / row["sku"].weight_netto)
                else:
                    kg = ""
                    boxes_count = ""

                values = [
                    batch_id,
                    row["sku_name"],
                    row["sku"].code,
                    row["sku"].in_box,
                    kg,
                    boxes_count,
                    row["start"],
                    row["finish"],
                ]
                df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)
        df_task = df_task[columns]  # fix order just in case
        df_task.to_csv(path, index=False, sep=";")

    def update_total_schedule_task(self):
        data_dir = create_dir(
            self.date.strftime(flask.current_app.config["DATE_FORMAT"]), flask.current_app.config["TASK_FOLDER"]
        )
        path = os.path.join(data_dir, f"{self.date.date()}.csv")
        columns = ["sku", "code", "in_box", "kg", "boxes_count"]
        if not os.path.exists(path):
            df_task = pd.DataFrame(columns=columns)
            df_task.to_csv(path, index=False, sep=";")

        df_task = pd.read_csv(path, sep=";")

        sku_names = db.session.query(self.model).all()
        sku_names = [x.name for x in sku_names]
        df_task = df_task[~df_task["sku"].isin(sku_names)]

        for sku_name, grp in self.df.groupby("sku_name"):
            kg = round(grp["kg"].sum())
            boxes_count = math.ceil(grp["kg"].sum() / grp.iloc[0]["sku"].in_box / grp.iloc[0]["sku"].weight_netto)
            values = [sku_name, grp.iloc[0]["sku"].code, grp.iloc[0]["sku"].in_box, kg, boxes_count]
            df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)
        df_task = df_task[columns]  # fix order just in case
        df_task.to_csv(path, index=False, sep=";")

    def draw_task_original(self, excel_client, cur_row, task_name):
        df_filter = self.df
        index = 1

        cur_row, excel_client = draw_header(excel_client, self.date, cur_row, task_name)

        for sku_name, grp in df_filter.groupby("sku_name"):
            kg = round(grp["kg"].sum())
            boxes_count = math.ceil(grp["kg"].sum() / grp.iloc[0]["sku"].in_box / grp.iloc[0]["sku"].weight_netto)
            values = [
                index,
                sku_name,
                grp.iloc[0]["sku"].in_box,
                kg,
                boxes_count,
                grp.iloc[0]["sku"].code,
            ]
            excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
            index += 1
        return cur_row

    def draw_task_boiling(self, excel_client, cur_row, task_name):
        cur_row, excel_client = draw_header(excel_client, self.date, cur_row, task_name, "варки")
        for batch_id, grp in self.df.groupby("absolute_batch_id"):
            for i, row in grp.iterrows():
                if row["sku"].group.name != "Качокавалло":
                    kg = round(row["original_kg"])
                    boxes_count = math.ceil(row["original_kg"] / row["sku"].in_box / row["sku"].weight_netto)
                else:
                    kg = ""
                    boxes_count = ""

                values = [
                    batch_id,
                    row["sku_name"],
                    row["sku"].in_box,
                    kg,
                    boxes_count,
                    row["sku"].code,
                ]
                excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
            excel_client = draw_blue_line(excel_client, cur_row)
            cur_row += 1
        return cur_row

    def schedule_task_original(self, wb, sheet_name="Печать заданий", cur_row=2):
        task_name = f"Задание на упаковку {self.department}"

        space_row = 4

        if sheet_name not in wb.sheetnames:
            wb.create_sheet(sheet_name)
        excel_client = ExcelBlock(wb[sheet_name], font_size=9)

        cur_row = self.draw_task_original(
            excel_client,
            cur_row,
            task_name,
        )
        cur_row += space_row
        return wb, cur_row

    def schedule_task_boilings(self, wb, sheet_name="Печать заданий 2", cur_row=2):
        task_name = f"Задание на упаковку {self.department}"

        space_row = 4

        if sheet_name not in wb.sheetnames:
            wb.create_sheet(sheet_name)
        excel_client = ExcelBlock(wb[sheet_name], font_size=9)

        cur_row = self.draw_task_boiling(
            excel_client,
            cur_row,
            task_name,
        )
        cur_row += space_row
        return wb, cur_row

    def update_schedule_task(self):
        self.update_boiling_schedule_task()
        self.update_total_schedule_task()
