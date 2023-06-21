from app.scheduler.adygea.tests.test_frontend import test_batch as test_adygea_batch


from app.scheduler.butter.tests.test_frontend import test_batch as test_butter_batch

from app.scheduler.mascarpone.tests.test_frontend import (
    test_batch as test_mascarpone_batch,
)

from app.scheduler.milk_project.tests.test_frontend import (
    test_batch as test_milk_project_batch,
)


from app.scheduler.ricotta.tests.test_frontend import test_batch as test_ricotta_batch

from app.scheduler.contour_cleanings.tests.test_frontend import (
    test_batch as test_contour_cleanings_batch,
)


if __name__ == "__main__":
    # todo later: restore mozzarella tests
    # test_mozzarella_batch()
    test_mascarpone_batch()
    test_ricotta_batch()
    test_butter_batch()
    test_adygea_batch()
    test_milk_project_batch()
    test_contour_cleanings_batch()

    # todo maybe: restore tests
    # test_mozzarella_parser_batch()
    # test_mozzarella_properties_batch()
