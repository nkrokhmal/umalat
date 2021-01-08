import os
import inspect
from flask_migrate import Migrate, MigrateCommand
from flask_admin import Admin
from flask_script import Manager
from flask_admin.contrib.sqla import ModelView

from app import create_app
import app.models as umalat_models

os.environ['environment'] = 'flask_app'

app, db = create_app()
manager = Manager(app)
migrate = Migrate(app, db, render_as_batch=True)
manager.add_command('db', MigrateCommand)

admin = Admin(app, name='Umalat admin', template_mode='bootstrap3')
for name, obj in inspect.getmembers(umalat_models):
    if inspect.isclass(obj):
        admin.add_view(ModelView(obj, db.session))

if __name__ == '__main__':
    # manager.run()
    app.run(port=5000, debug=True, threaded=True, host='0.0.0.0')