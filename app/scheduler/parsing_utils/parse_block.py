from typing import Callable

import pandas as pd

from utils_ak.block_tree import BlockMaker, add_push

from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.parsing_utils.group_neighbor_intervals import group_neighbor_intervals
from app.scheduler.parsing_utils.load_cells_df import load_cells_df


def parse_block(
    m: BlockMaker,
    cells_df: pd.DataFrame,
    label: str,
    element_label: str,
    rows: list,
    start_time,
    length: int = 2,
    split_func: Callable = None,
    filter_: Callable = None,
):
    with m.row(label, x=start_time, push_func=add_push):
        for i, row_num in enumerate(rows):
            df1 = cells_df[(cells_df["x1"] == row_num) & (cells_df["x0"] >= 4)]  # filter column header
            groups = group_neighbor_intervals(
                [row for i, row in df1.iterrows()],
                max_group_size=length,
                interval_func=lambda row: [row["x0"], row["y0"]],
                split_func=split_func,
            )

            for group in groups:
                if filter_ and not filter_(group):
                    continue

                try:
                    boiling_id = int(group[0]["label"].split(" ")[0])
                except Exception as e:
                    boiling_id = None

                m.row(
                    element_label,
                    size=group[-1]["y0"] - group[0]["x0"],
                    x=group[0]["x0"] - 5,  # subtract column header
                    boiling_id=boiling_id,
                    line_num=str(i),
                    row_num=row_num,
                    group=group,
                    label=str(boiling_id),
                    push_func=add_push,
                )


def test():
    cells_df = load_cells_df(
        str(
            get_repo_path()
            / "app/data/static/samples/by_department/mozzarella/План по варкам моцарелла 4 расписание.xlsx"
        ),
        "Расписание",
    )

    parse_block(
        m=BlockMaker(),
        cells_df=cells_df,
        label="boiling",
        element_label="element",
        rows=[5, 6],
        start_time=0,
        length=2,
    )


if __name__ == "__main__":
    test()
