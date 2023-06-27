from app.imports.runtime import *
from app.scheduler.parsing_new.parse_time import *
from app.enum import LineName
from utils_ak.block_tree import *


def prepare_boiling_plan(parsed_schedule, df_bp):
    df_bp["line_name"] = df_bp["line"].apply(lambda line: line.name)
    for line_name, grp_line in df_bp.groupby("line_name"):
        if line_name == LineName.WATER:
            boiling_ids = [b.props["label"] for b in parsed_schedule["water_packings"].children]
        else:
            boiling_ids = [b.props["label"] for b in parsed_schedule["salt_packings"].children]

        boiling_ids = list(sorted(set(boiling_ids)))

        if len(boiling_ids) != len(grp_line["group_id"].unique()):
            raise Exception(
                f'Wrong number of boiling ids: {len(boiling_ids)}, should be: {len(grp_line["group_id"].unique())}'
            )

        for i, (_, grp) in enumerate(grp_line.groupby("group_id")):
            df_bp.loc[grp.index, "boiling_id"] = boiling_ids[i]
    df_bp["boiling_id"] = df_bp["boiling_id"].astype(int)
    return df_bp
