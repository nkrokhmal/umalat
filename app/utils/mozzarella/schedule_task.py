from app.utils.base.schedule_task import *
from app.models.mozzarella import MozzarellaSKU


class MozzarellaScheduleTask(BaseScheduleTask[MozzarellaSKU]):
    def update_boiling_schedule_task(self, batch_number):
        data_dir = create_dir(
            self.date.strftime(flask.current_app.config["DATE_FORMAT"]),
            "task"
        )
        path = os.path.join(data_dir, f"{self.date.date()} {self.department}.csv")
        columns = ["batch", "sku", "code", "in_box", "kg", "boxes_count"]
        if not os.path.exists(path):
            df_task = pd.DataFrame(columns=columns)
            df_task.to_csv(path, index=False, sep=";")

        df_task = pd.read_csv(path, sep=";")
        df_task.drop(df_task.index, inplace=True)

        for boiling_group_id, grp in self.df.groupby("group_id"):
            for i, row in grp.iterrows():
                if row["sku"].group.name != "Качокавалло":
                    kg = round(row["original_kg"])
                    boxes_count = math.ceil(
                        1000
                        * row["original_kg"]
                        / row["sku"].in_box
                        / row["sku"].weight_netto
                    )
                else:
                    kg = ""
                    boxes_count = ""

                values = [
                    boiling_group_id + batch_number - 1,
                    row["sku_name"],
                    row["sku"].code,
                    row["sku"].in_box,
                    kg,
                    boxes_count,
                ]
                df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)

        if self.df_packing is not None:
            for i, row in self.df_packing.iterrows():
                kg = round(row["kg"])
                boxes_count = math.ceil(
                    1000 * row["kg"] / row["sku_obj"].in_box / row["sku_obj"].weight_netto
                )
                values = [
                    "",
                    row["sku"],
                    row["sku_obj"].code,
                    row["sku_obj"].in_box,
                    kg,
                    boxes_count,
                ]
                df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)

        df_task.to_csv(path, index=False, sep=";")

    def update_total_schedule_task(self):
        data_dir = create_dir(
            self.date.strftime(flask.current_app.config["DATE_FORMAT"]),
            "task"
        )
        path = os.path.join(data_dir, f"{self.date.date()}.csv")
        columns = ["sku", "code", "in_box", "kg", "boxes_count"]
        if not os.path.exists(path):
            df_task = pd.DataFrame(columns=columns)
            df_task.to_csv(path, index=False, sep=";")

        df_task = pd.read_csv(path, sep=";")

        sku_names = db.session.query(self.model).all()
        sku_names = [x.name for x in sku_names]
        df_task = df_task[~df_task['sku'].isin(sku_names)]

        for sku_name, grp in self.df.groupby("sku_name"):
            if grp.iloc[0]["sku"].group.name != "Качокавалло":
                kg = round(grp["original_kg"].sum())
                boxes_count = math.ceil(
                    1000
                    * grp["original_kg"].sum()
                    / grp.iloc[0]["sku"].in_box
                    / grp.iloc[0]["sku"].weight_netto
                )
                values = [
                    sku_name,
                    grp.iloc[0]["sku"].code,
                    grp.iloc[0]["sku"].in_box,
                    kg,
                    boxes_count,
                ]
                df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)

        skus = df_task.sku.values
        if self.df_packing is not None:
            for i, row in self.df_packing.iterrows():
                boxes_count = math.ceil(
                    1000 * row["kg"] / row["sku_obj"].in_box / row["sku_obj"].weight_netto
                )
                values = [
                    row["sku"],
                    row["sku_obj"].code,
                    row["sku_obj"].in_box,
                    row["kg"],
                    boxes_count,
                ]
                if row["sku"] in skus:
                    df_task.loc[df_task.sku == values[0], columns] = values
                else:
                    df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)

        df_task.to_csv(path, index=False, sep=";")

    def draw_task_original(self, excel_client, cur_row, task_name, line_name, draw_packing=True):
        df_filter = self.df[self.df["line"] == line_name]
        index = 1

        cur_row, excel_client = draw_header(excel_client, self.date, cur_row, task_name)

        for sku_name, grp in df_filter.groupby("sku_name"):
            if grp.iloc[0]["sku"].group.name != "Качокавалло":
                kg = round(grp["original_kg"].sum())
                boxes_count = math.ceil(
                    1000
                    * grp["original_kg"].sum()
                    / grp.iloc[0]["sku"].in_box
                    / grp.iloc[0]["sku"].weight_netto
                )
            else:
                kg = ""
                boxes_count = ""
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

        if self.df_packing is not None:
            if draw_packing:
                for i, row in self.df_packing.iterrows():
                    boxes_count = math.ceil(
                        1000 * row["kg"] / row["sku_obj"].in_box / row["sku_obj"].weight_netto
                    )
                    values = [
                        index,
                        row["sku"],
                        row["sku_obj"].in_box,
                        row["kg"],
                        boxes_count,
                        row["sku_obj"].code,
                    ]
                    excel_client, cur_row = draw_schedule_raw(
                        excel_client, cur_row, values, COLOR_PACKING
                    )
                    index += 1
                    index += 1

        return cur_row

    def draw_task_boiling(
            self, excel_client, cur_row, task_name, batch_number, line_name, draw_packing=True
    ):
        df_filter = self.df[self.df["line"] == line_name]

        cur_row, excel_client = draw_header(excel_client, self.date, cur_row, task_name, "варки")
        for boiling_group_id, grp in df_filter.groupby("group_id"):
            for i, row in grp.iterrows():
                if row["sku"].group.name != "Качокавалло":
                    kg = round(row["original_kg"])
                    boxes_count = math.ceil(
                        1000
                        * row["original_kg"]
                        / row["sku"].in_box
                        / row["sku"].weight_netto
                    )
                else:
                    kg = ""
                    boxes_count = ""

                values = [
                    boiling_group_id + batch_number - 1,
                    row["sku_name"],
                    row["sku"].in_box,
                    kg,
                    boxes_count,
                    row["sku"].code,
                ]
                excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
            excel_client = draw_blue_line(excel_client, cur_row)
            cur_row += 1

        if self.df_packing is not None:
            if draw_packing:
                for i, row in self.df_packing.iterrows():
                    kg = round(row["kg"])
                    boxes_count = math.ceil(
                        1000 * row["kg"] / row["sku_obj"].in_box / row["sku_obj"].weight_netto
                    )
                    values = [
                        "",
                        row["sku"],
                        row["sku_obj"].in_box,
                        kg,
                        boxes_count,
                        row["sku_obj"].code,
                    ]
                    excel_client, cur_row = draw_schedule_raw(
                        excel_client, cur_row, values, COLOR_PACKING
                    )

            _ = draw_blue_line(excel_client, cur_row)
            cur_row += 1

        return cur_row

    def schedule_task_original(self, wb):
        sheet_name = "Печать заданий"
        water_task_name = f"Задание на упаковку линии воды {self.department}"
        salt_task_name = f"Задание на упаковку линии пиццы {self.department}"

        cur_row = 2
        space_row = 4

        wb.create_sheet(sheet_name)
        excel_client = ExcelBlock(wb[sheet_name], font_size=9)

        cur_row = self.draw_task_original(
            excel_client,
            cur_row,
            water_task_name,
            LineName.WATER,
            draw_packing=False,
        )
        cur_row += space_row

        _ = self.draw_task_original(
            excel_client,
            cur_row,
            salt_task_name,
            LineName.SALT,
        )
        return wb

    def schedule_task_boilings(self, wb, batch_number):
        sheet_name = "Печать заданий 2"
        water_task_name = f"Задание на упаковку линии воды {self.department}"
        salt_task_name = f"Задание на упаковку линии пиццы {self.department}"

        cur_row = 2
        space_row = 4

        wb.create_sheet(sheet_name)
        excel_client = ExcelBlock(wb[sheet_name], font_size=9)

        cur_row = self.draw_task_boiling(
            excel_client,
            cur_row,
            water_task_name,
            batch_number,
            LineName.WATER,
            draw_packing=False,
        )
        cur_row += space_row

        _ = self.draw_task_boiling(
            excel_client,
            cur_row,
            salt_task_name,
            batch_number,
            LineName.SALT,
        )
        return wb




