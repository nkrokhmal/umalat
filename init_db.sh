rm data.sqlite && rm -rf migrations && python3 manage.py db init && python3 manage.py db migrate && python3 manage.py db upgrade && python3 fill_db.py  
