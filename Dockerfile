FROM python:3.11-bullseye
RUN apt-get update && apt-get install -y gettext binutils libproj-dev gdal-bin
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG USER_ID
ARG GROUP_ID
RUN groupadd -o -g $GROUP_ID -r usergrp
RUN useradd -o -m -u $USER_ID -g $GROUP_ID user
RUN mkdir /code
RUN chown user /code
ENV PATH="${PATH}:/home/user/.local/bin"
USER user
WORKDIR /code
COPY requirements /code/requirements
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
