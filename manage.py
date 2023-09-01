import os


os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import create_app, create_manager


app, rq = create_app()
create_manager(app)


if __name__ == "__main__":
    app.run()
