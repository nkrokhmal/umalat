from app.models import *
from app.scheduler.mascarpone.algo.cream_cheese_boilings import *


def test_make_mascarpone_boiling():
    utils.lazy_tester.configure_function_path()
    sku = cast_model(CreamCheeseSKU, 'Кремчиз "Unagrande", 70%, 0,5 кг, пл/с')
    values = [[0, sku, 10]]
    boiling_group_df = pd.DataFrame(values, columns=["boiling_id", "sku", "kg"])
    utils.lazy_tester.log(make_cream_cheese_boiling(boiling_group_df))

    utils.lazy_tester.assert_logs()


if __name__ == "__main__":
    test_make_mascarpone_boiling()
