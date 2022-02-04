import os

os.environ["ENVIRONMENT"] = "production"
os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import *

app, rq = create_app()
manager = create_manager(app)

if __name__ == "__main__":
    utils.configure_loguru_stdout("DEBUG")
    app.run(port=5000, threaded=True, host="0.0.0.0")
