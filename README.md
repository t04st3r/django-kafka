[![CircleCI](https://circleci.com/gh/t04st3r/django-kafka.svg?style=shield)](https://app.circleci.com/pipelines/github/t04st3r/django-kafka) [![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)


# Django-Kafka
This is a sample project on how to use Django with Apache Kafka to produce and consume streaming events.

## Install
To run django locally you need python version to `3.11.3` and pipenv, you can use [pyenv](https://github.com/pyenv/pyenv) to set your desired python version.

### Run containers
Django needs postgres, redis, kafka and zookeeper container to be
up and running, to do so clone the project, enter in the project folder and hit:
```bash
docker compose up postgres redis kafka zookeeper
```

### Install django deps and run django server
inside the project folder make user you use python 3.11.3
```bash
python --version
```
you should see
```bash
Python 3.11.3
```
install requirements (listed inside `Pipfile`) by
```bash
pipenv install
```
To run tests you will need also dev dependencies
```bash
pipenv install --dev
```
Create a `.env` file using the `.env.example` file and changing the url to be `localhost` in the following env variables
```env
KAFKA_BROKER_URL
POSTGRES_HOST
REDIS_URL
```
Your `.env` file should be something like this
```env
#django
ENV=dev
DJANGO_DEBUG=True
SECRET_KEY='supersecretkey'
KAFKA_BROKER_URL=localhost:29092
KAFKA_BROKER_TOPIC=public_holiday

#db
POSTGRES_USER=postgres
POSTGRES_DB=app_db
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=password
POSTGRES_PORT=5432

#redis
REDIS_URL=redis://localhost:6379/0

#zookeeper
ZOOKEEPER_CLIENT_PORT=2181
ZOOKEEPER_TICK_TIME=2000

#kafka
KAFKA_BROKER_ID=1
KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1
```

Once done enter inside your pipenv virtual environment by
```bash
pipenv shell
```
Run migrations with
```bash 
python manage.py migrate
```
Or (if you have `make` installed) by
```bash
make migrate
```
Everything is done! You can now start the server with
```bash
python manage.py runserver
```
Or
```bash
make run-dev
```
## How does it works
This apps gather data from [Public Holiday API](https://date.nager.at/Api) via a django command, you can populate PublicHoliday models with
```bash
python manage.py populate_models
```
Or
```bash
make populate-models
```
For each command run a random country is selected and all the public holidays for that country would be fetched and stored in the db

## Producer and Consumer

To run a Consumer that will consume event (in this case it would be simply printed in the stdout of the django command) run the following django command

```bash
python manage.py consume_records
```
Or
```bash
make consume-records
```
If the topic the consumer will listen to has not been created yet you can do so by
```bash
docker exec -it django-kafka-kafka-1 kafka-topics --create --topic public_holiday --bootstrap-server localhost:29092
```


Through the `/producer/` endpoint the last 10 recently added models would be published as JSON message in the `public_holiday` topic inside Kafka. 
To produce some records in the `public_holiday` topic simply reach `http://localhost:8000/producer/` with your browser

Once produced you should see that the message has been consumed by the consumer command output logs.

## Testing
You can run django tests by simply run
```bash
pytest
```
To simulate the [testing pipeline](https://app.circleci.com/pipelines/github/t04st3r/django-kafka) in CircleCI just run
```bash
docker compose run django test
```