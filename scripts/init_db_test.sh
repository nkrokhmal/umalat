FLASK_APP=runserver_test.py; echo $FLASK_APP
cd .. && rm -f db/test/data.sqlite && rm -r -f db/test/migrations && flask db init --directory db/test/migrations && flask db migrate && flask db upgrade && python db/fill_db_test.py
