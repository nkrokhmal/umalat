del "data.sqlite"
rmdir /s /q "migrations/"
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python fill_db.py