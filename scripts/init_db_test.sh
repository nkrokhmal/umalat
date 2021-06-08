cd .. &&
rm -f db/test/data.sqlite &&
rm -r -f db/test/migrations &&
python3 manage_test.py db init --directory db/test/migrations &&
python3 manage_test.py db migrate &&
python3 manage_test.py db upgrade &&
python3 db/fill_db_test.py
