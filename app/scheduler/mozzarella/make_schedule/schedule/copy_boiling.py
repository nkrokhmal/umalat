from copy import deepcopy


def copy_boiling(boiling):
    props = boiling.props.all()

    new_boiling = deepcopy(boiling)

    new_boiling.props.update(boiling_group_df=props["boiling_group_df"], boiling_model=props["boiling_model"])
    return new_boiling
