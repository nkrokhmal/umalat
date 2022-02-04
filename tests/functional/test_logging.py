

from app.imports.runtime import *


def test_logging():
    logger.debug("Debug")
    logger.info("Info")
    logger.warning("Warning")
    logger.error("Error")
    logger.critical("Critical", some_variable=1)

    @logger.catch()
    def f(x=2):
        1 / 0

    f()

    try:
        1 / 0
    except:
        logger.exception("Exception")

if __name__ == '__main__':
    test_logging()