import os

from loguru import logger


os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import create_app


app, rq = create_app()


@app.cli.command("run_worker")
def run_worker():
    logger.info("Running worker")
    default_worker = rq.get_worker()
    default_worker.work()


if __name__ == "__main__":
    app.run()
