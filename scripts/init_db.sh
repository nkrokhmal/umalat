cd .. && rm -f db/data.sqlite && rm -r -f db/migrations && python3 manage.py db init --directory db/migrations && python3 manage.py db migrate && python3 manage.py db upgrade && python3 db/fill_db.py
