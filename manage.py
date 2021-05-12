from app.imports.external import *

os.environ["environment"] = "flask_app"

from app.app import *

app = create_app()
manager = create_manager(app)

if __name__ == "__main__":
    manager.run()
