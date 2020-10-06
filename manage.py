from flask_migrate import Migrate, MigrateCommand

from app import create_app
from flask_script import Manager

app, db = create_app()
manager = Manager(app)
migrate = Migrate(app, db)

# manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    app.run(port=5000, debug=True, threaded=True, host='0.0.0.0')