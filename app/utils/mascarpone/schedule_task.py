from app.models import MascarponeSKU
from app.utils.base.schedule_task import BaseScheduleTask
from app.utils.files.utils import create_dir
from app.imports.runtime import *
from app.utils.features.draw_utils import *


# todo maybe: possible
class MascarponeScheduleTask(BaseScheduleTask[MascarponeSKU]):
    def update_boiling_schedule_task(self):
        data_dir = create_dir(
            self.date.strftime(flask.current_app.config["DATE_FORMAT"]),
            flask.current_app.config["TASK_FOLDER"]
        )
        path = os.path.join(data_dir, f"{self.date.date()} {self.department}.csv")
        columns = ["batch", "sku", "code", "in_box", "kg", "boxes_count", 'start', 'finish']
        if not os.path.exists(path):
            df_task = pd.DataFrame(columns=columns)
            df_task.to_csv(path, index=False, sep=";")

        df_task = pd.read_csv(path, sep=";")
        df_task.drop(df_task.index, inplace=True)
        self.df["coeff"] = self.df["boiling"].apply(lambda x: x.output_coeff)
        for _, group_df in self.df.groupby("batch_type"):
            for batch_id, grp in group_df.groupby("absolute_batch_id"):
                for i, row in grp.iterrows():
                    kg = round(row["original_kg"] * row["coeff"])
                    boxes_count = math.ceil(
                        row["original_kg"]
                        / row["sku"].in_box
                        / row["sku"].weight_netto
                    )

                    values = [
                        batch_id,
                        row["sku_name"],
                        row["sku"].code,
                        row["sku"].in_box,
                        kg,
                        boxes_count,
                        row['start'],
                        row['finish']
                    ]
                    df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)
        df_task = df_task[columns] # fix order just in case
        df_task.to_csv(path, index=False, sep=";")

    def draw_task_original(self, excel_client, cur_row, task_name):
        df_filter = self.df
        index = 1

        cur_row, excel_client = draw_header(excel_client, self.date, cur_row, task_name)

        self.df["coeff"] = self.df["boiling"].apply(lambda x: x.output_coeff)
        for sku_name, grp in df_filter.groupby("sku_name"):
            kg = round((grp["kg"] * grp["coeff"]).sum())
            boxes_count = math.ceil(
                grp["kg"].sum()
                / grp.iloc[0]["sku"].in_box
                / grp.iloc[0]["sku"].weight_netto
            )
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