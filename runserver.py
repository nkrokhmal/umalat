import os


os.environ["ENVIRONMENT"] = "production"
os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import create_app, create_manager


app, rq = create_app()
create_manager(app)

if __name__ == "__main__":
    app.run(port=5000, threaded=False, host="0.0.0.0", debug=True)
