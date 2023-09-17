from dataclasses import dataclass

import pytest

from app.utils.base.boiling_group import BoilingGroup
from app.utils.mascarpone.utils import MascarponeBoilingsHandler


def test_boiling_group_no_exception() -> None:
    """
    No exception boiling group tests:
    - Correct leftovers
    - Correct is full check
    """
    group = BoilingGroup(weight=100)
    assert group.leftovers == 100
    assert not group.is_full

    group.add_sku(dict(plan=30))
    assert group.leftovers == 70
    assert not group.is_full

    group.add_sku(dict(weight=70), weight_key="weight")
    assert group.leftovers == 0
    assert group.is_full


def test_boiling_group_exception() -> None:
    """
    Boiling group exceptions test:
    - Can't add heavy sku
    """
    group = BoilingGroup(weight=100)

    with pytest.raises(ValueError):
        group.add_sku(dict(plan=110))

    group.add_sku(dict(plan=30))
    assert group.leftovers == 70

    with pytest.raises(ValueError):
        group.add_sku(dict(weight=71), weight_key="weight")


@dataclass
class HandlerCase:
    groups: list[dict]
    ground_truth: list[list[dict]]


CASES: list[HandlerCase] = [
    HandlerCase(
        groups=[{"max_weight": 100, "skus": [{"name": 0, "plan": 300}]}],
        ground_truth=[
            [{"name": 0, "plan": 100, "id": 0}],
            [{"name": 0, "plan": 100, "id": 1}],
            [{"name": 0, "plan": 100, "id": 2}],
        ],
    ),
    HandlerCase(
        groups=[{"max_weight": 100, "skus": [{"name": 0, "plan": 20}, {"name": 1, "plan": 100}]}],
        ground_truth=[
            [{"name": 0, "plan": 20, "id": 0}, {"name": 1, "plan": 80, "id": 0}],
            [{"name": 1, "plan": 20, "id": 1}],
        ],
    ),
    HandlerCase(
        groups=[
            {"max_weight": 100, "skus": [{"name": 0, "plan": 20}, {"name": 1, "plan": 110}, {"name": 2, "plan": 70}]},
            {"max_weight": 50, "skus": [{"name": 3, "plan": 70}]},
        ],
        ground_truth=[
            [{"name": 0, "plan": 20, "id": 0}, {"name": 1, "plan": 80, "id": 0}],
            [{"name": 1, "plan": 30, "id": 1}, {"name": 2, "plan": 70, "id": 1}],
            [{"name": 3, "plan": 50, "id": 2}],
            [{"name": 3, "plan": 20, "id": 3}],
        ],
    ),
]


@pytest.mark.parametrize("case", CASES)
def test_boiling_handler(case: HandlerCase) -> None:
    handler = MascarponeBoilingsHandler()
    for group in case.groups:
        handler.handle_group(skus=group["skus"], max_weight=group["max_weight"])

    assert len(handler.boilings) == handler.boiling_id == len(case.ground_truth)

    for i, boiling in enumerate(handler.boilings):
        assert boiling.id == i
        assert boiling.skus == case.ground_truth[i]
