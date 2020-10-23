from flask_migrate import Migrate, MigrateCommand
from flask_admin import Admin
from app import create_app
from flask_script import Manager
from flask_admin.contrib.sqla import ModelView
import sys, inspect


# from app.models import Boiling, MeltingProcess, SKU
import app.models as umalat_models

app, db = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


admin = Admin(app, name='Umalat admin', template_mode='bootstrap3')
for name, obj in inspect.getmembers(umalat_models):
    if inspect.isclass(obj):
        admin.add_view(ModelView(obj, db.session))

# admin.add_view(ModelView(Boiling, db.session))
# admin.add_view(ModelView(MeltingProcess, db.session))
# admin.add_view(ModelView(SKU, db.session))
# admin.add_view(ModelView(db.session))

if __name__ == '__main__':
    manager.run()
    # app.run(port=5000, debug=True, threaded=True, host='0.0.0.0')