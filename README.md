# Library-service

API service for online management system for book borrowings written on DRF

## Installing using GitHub


```shell
git clone https://github.com/Tania-Kharchuk/library-service
cd library-service
- Create venv:
python -m venv venv
- Activate venv:
source venv/bin/activate
- Install requirements:
pip install -r requirements.txt
- Create new Postgres DB and user
- Copy .env.sample and populate with all required data
python manage.py migrate
- Run Redis server:
docker run -d -p 6379:6379 redis
- Run celery worker for tasks handling:
celery -A library_service worker -l INFO
- Run celery beat for tasks scheduling:
celery -A library_service beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
python manage.py runserver
```

## Run with Docker

```shell
- Copy .env.sample and populate with all required data
docker-compose build
docker-compose up
```

## Getting access

* create user via api/user/register
* get access token via api/user/token

## Features

* JWT authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Manage books inventory
* Manage books borrowing
* Manage customers
* Display notifications
* Handle payments

