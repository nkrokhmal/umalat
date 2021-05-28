import os

os.environ["environment"] = "interactive"
from app.models import *

from app.scheduler.ricotta.algo.boilings import *
from app.scheduler.ricotta.boiling_plan import *


def test_make_boiling():
    boiling_model = cast_model(RicottaBoiling, 9)
    print(make_boiling(boiling_model))


def test_make_boiling_sequence():
    boiling_plan_df = generate_random_boiling_plan()
    boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == 0]
    print(make_boiling_sequence(boiling_group_df))


def test_make_boiling_group():
    boiling_plan_df = generate_random_boiling_plan()
    boiling_group_df = boiling_plan_df[boiling_plan_df["boiling_id"] == 0]
    print(make_boiling_group(boiling_group_df))


if __name__ == "__main__":
    test_make_boiling()
    # test_make_boiling_sequence()
    # test_make_boiling_group()
