import os

os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import *

app, rq = create_app()
manager = create_manager(app)


if __name__ == "__main__":
    app.run(port=5000, threaded=True, host="0.0.0.0")
