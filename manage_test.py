import os


os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import *


app, rq = create_app("test")
manager = create_manager(app)

if __name__ == "__main__":
    manager.run()
