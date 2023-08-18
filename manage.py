import os

from app.create_manager import create_manager


os.environ["APP_ENVIRONMENT"] = "runtime"

from app.create_app import *


app, rq = create_app()
manager = create_manager(app)


@manager.command
def run_worker():
    default_worker = rq.get_worker()
    default_worker.work()


if __name__ == "__main__":
    manager.run()
