cd .. && rm -f db/prod/data.sqlite && rm -r -f db/prod/migrations && flask db init --directory db/prod/migrations && flask db migrate && flask db upgrade && python db/fill_db.py
