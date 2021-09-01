from app.models import MascarponeSKU
from app.utils.base.schedule_task import BaseScheduleTask
from app.utils.files.utils import create_dir
from app.imports.runtime import *


class MascarponeScheduleTask(BaseScheduleTask[MascarponeSKU]):
    def update_boiling_schedule_task(self, batch_number):
        data_dir = create_dir(
            self.date.strftime(flask.current_app.config["DATE_FORMAT"]),
            flask.current_app.config["TASK_FOLDER"]
        )
        path = os.path.join(data_dir, f"{self.date.date()} {self.department}.csv")
        columns = ["batch", "sku", "code", "in_box", "kg", "boxes_count"]
        if not os.path.exists(path):
            df_task = pd.DataFrame(columns=columns)
            df_task.to_csv(path, index=False, sep=";")

        df_task = pd.read_csv(path, sep=";")
        df_task.drop(df_task.index, inplace=True)

        for boiling_group_id, grp in self.df.groupby("batch_id"):
            for i, row in grp.iterrows():
                kg = round(row["original_kg"])
                boxes_count = math.ceil(
                    row["original_kg"]
                    / row["sku"].in_box
                    / row["sku"].weight_netto
                )

                values = [
                    boiling_group_id + batch_number - 1,
                    row["sku_name"],
                    row["sku"].code,
                    row["sku"].in_box,
                    kg,
                    boxes_count,
                ]
                df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)
        df_task.to_csv(path, index=False, sep=";")
