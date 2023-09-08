import os


os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import create_app, create_manager


app, rq = create_app()
create_manager(app)


@app.cli.command("run_worker")
def run_worker():
    default_worker = rq.get_worker()
    default_worker.work()


if __name__ == "__main__":
    app.run()
