web: gunicorn csv_data_gen.wsgi
worker: celery worker --app
release: python manage.py migrate