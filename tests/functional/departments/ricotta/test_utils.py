dataclass


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
    handler = BoilingsHandler()
    for group in case.groups:
        handler.handle_group(skus=group["skus"], max_weight=group["max_weight"])

    assert len(handler.boilings) == handler.boiling_id == len(case.ground_truth)

    for i, boiling in enumerate(handler.boilings):
        assert boiling.id == i
        assert boiling.skus == case.ground_truth[i]
