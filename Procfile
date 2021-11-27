web: gunicorn csv_data_gen.wsgi
celery: celery -A csv_data_gen worker -l INFO
release: python manage.py migrate