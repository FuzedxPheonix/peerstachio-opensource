## Django Development With Docker Compose

Featuring:

- Docker 17.12.1-ce
- Docker Compose 1.21.2
- Python 3.6.5
- Django 2.0.6


`docker-compose build`

`docker-compose up -d`

`docker-compose run web /usr/local/bin/python manage.py migrate`

GET IP ADDRESS: `docker inspect -f '\''{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}} NAME_OF_CONTAINER(_web_1)`
(not necessary anymore, now binds to localhost)


`docker-compose down`