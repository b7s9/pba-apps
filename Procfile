release: python manage.py migrate
web: gunicorn -c gunicorn.conf.py pbaabp.asgi --bind :$PORT --access-logfile - --error-logfile - --workers 2 --max-requests 60 --max-requests-jitter 10
worker: python -m celery -A pbaabp worker -c 1 --beat -l INFO
discordworker: python manage.py run_discord
