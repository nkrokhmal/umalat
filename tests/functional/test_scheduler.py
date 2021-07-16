from app.scheduler.mozzarella.tests.test_frontend import (
    test_batch as test_mozzarella_batch,
)
from app.scheduler.mascarpone.tests.test_frontend import (
    test_batch as test_mascarpone_batch,
)
from app.scheduler.ricotta.tests.test_frontend import test_batch as test_drawing_ricotta

if __name__ == "__main__":
    test_mozzarella_batch()
    test_mascarpone_batch()
    test_drawing_ricotta()
