from dataclasses import dataclass

import pytest

from app.utils.ricotta.utils import RicottaBoilingsHandler


@dataclass
class HandlerCase:
    groups: list[dict]
    ground_truth: list[list[dict]]
    counts: list[int]


CASES: list[HandlerCase] = [
    HandlerCase(
        groups=[{"max_weight": 100, "skus": [{"name": 0, "plan": 300}]}],
        ground_truth=[
            [{"name": 0, "plan": 100, "id": 0}],
        ],
        counts=[3],
    ),
    HandlerCase(
        groups=[{"max_weight": 100, "skus": [{"name": 0, "plan": 220}, {"name": 1, "plan": 100}]}],
        ground_truth=[
            [{"name": 0, "plan": 100, "id": 0}],
            [{"name": 0, "plan": 20, "id": 2}, {"name": 1, "plan": 80, "id": 2}],
            [{"name": 1, "plan": 20, "id": 3}],
        ],
        counts=[2, 1, 1],
    ),
    HandlerCase(
        groups=[
            {"max_weight": 100, "skus": [{"name": 0, "plan": 120}, {"name": 1, "plan": 110}, {"name": 2, "plan": 70}]},
            {"max_weight": 50, "skus": [{"name": 3, "plan": 70}]},
        ],
        ground_truth=[
            [{"name": 0, "plan": 100, "id": 0}],
            [{"name": 0, "plan": 20, "id": 1}, {"name": 1, "plan": 80, "id": 1}],
            [{"name": 1, "plan": 30, "id": 2}, {"name": 2, "plan": 70, "id": 2}],
            [{"name": 3, "plan": 50, "id": 3}],
            [{"name": 3, "plan": 20, "id": 4}],
        ],
        counts=[1, 1, 1, 1, 1],
    ),
]


@pytest.mark.parametrize("case", CASES)
def test_boiling_handler(case: HandlerCase) -> None:
    handler = RicottaBoilingsHandler()
    for group in case.groups:
        handler.handle_group(skus=group["skus"], max_weight=group["max_weight"])

    assert len(handler.boilings) == len(case.ground_truth)
    gt_boiling_id: int = 0

    for i, boiling in enumerate(handler.boilings):
        assert boiling.id == gt_boiling_id
        assert boiling.skus == case.ground_truth[i]
        assert boiling.count == case.counts[i]

        gt_boiling_id += case.counts[i]
