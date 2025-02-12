FROM python:3.11-bullseye
RUN apt-get update && apt-get install -y gettext binutils libproj-dev gdal-bin
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN mkdir /code
WORKDIR /code
COPY requirements /code/requirements
RUN pip install -r requirements/base.txt
RUN pip install -r requirements/deploy.txt
COPY . /code/
RUN \
    DJANGO_SECRET_KEY=deadbeefcafe \
    DATABASE_URL=None \
    RECAPTCHA_PRIVATE_KEY=None \
    RECAPTCHA_PUBLIC_KEY=None \
    DJANGO_SETTINGS_MODULE=pbaabp.settings \
    python manage.py collectstatic --noinput
