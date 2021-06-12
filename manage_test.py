import os

os.environ["ENVIRONMENT"] = "runtime"

from app.app import *

app = create_app("test")
manager = create_manager(app)

if __name__ == "__main__":
    manager.run()