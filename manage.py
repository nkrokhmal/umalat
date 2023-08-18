import os


os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import *


app, rq = create_app()
create_manager(app)


@manager.command
def run_worker():
    default_worker = rq.get_worker()
    default_worker.work()


if __name__ == "__main__":
    manager.run()
