import os

from app.create_manager import create_manager


os.environ["APP_ENVIRONMENT"] = "runtime"

from app.create_app import *


app, rq = create_app("test")
manager = create_manager(app)

if __name__ == "__main__":
    manager.run()
