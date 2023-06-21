from app.scheduler.adygea.tests.test_frontend import test_batch as test_adygea_batch

from app.scheduler.adygea.tests.test_properties import test_batch as test_adygea_properties_batch

from app.scheduler.butter.tests.test_frontend import test_batch as test_butter_batch
from app.scheduler.butter.tests.test_parser_new import test_batch as test_butter_parser_batch
from app.scheduler.butter.tests.test_properties import test_batch as test_butter_properties_batch

from app.scheduler.mascarpone.tests.test_frontend import (
    test_batch as test_mascarpone_batch,
)
from app.scheduler.mascarpone.tests.test_parser_new import (
    test_batch as test_mascarpone_parser_batch,
)
from app.scheduler.mascarpone.tests.test_properties import (
    test_batch as test_mascarpone_properties_batch,
)

from app.scheduler.milk_project.tests.test_frontend import (
    test_batch as test_milk_project_batch,
)
from app.scheduler.milk_project.tests.test_parser_new import (
    test_batch as test_milk_project_parser_batch,
)
from app.scheduler.milk_project.tests.test_properties import (
    test_batch as test_milk_project_properties_batch,
)


from app.scheduler.ricotta.tests.test_frontend import test_batch as test_ricotta_batch
from app.scheduler.ricotta.tests.test_parser_new import test_batch as test_ricotta_parser_batch
from app.scheduler.ricotta.tests.test_properties import test_batch as test_ricotta_properties_batch

from app.scheduler.contour_cleanings.tests.test_frontend import (
    test_batch as test_contour_cleanings_batch,
)



if __name__ == "__main__":
    # todo later: restore mozzarella
    # test_mozzarella_batch()
    test_mascarpone_batch()
    test_ricotta_batch()
    test_butter_batch()
    test_adygea_batch()
    test_milk_project_batch()
    test_contour_cleanings_batch()

    # todo later: restore
    # test_mozzarella_parser_batch()
    test_ricotta_parser_batch()
    test_butter_parser_batch()
    test_mascarpone_parser_batch()
    test_milk_project_parser_batch()

    # todo later: restore
    # test_mozzarella_properties_batch()
    test_ricotta_properties_batch()
    test_milk_project_properties_batch()
    test_mascarpone_properties_batch()
    test_butter_properties_batch()
    test_adygea_properties_batch()
