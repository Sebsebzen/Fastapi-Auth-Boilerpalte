# FastAPI + SQLModel + Alembic

FastAPI Auth boilerplate that uses SQLAlchemy, Postgres, Alembic, and Docker.

## Setup the project

Clone the repo

Add missing environment variables to `.env` file in `fastapi` folder

```sh
MAILGUN_EMAIL=<mailgun-email>
MAILGUN_PASSWORD=<mailgun-password>
```

then run

```sh
$ docker-compose up -d --build
```

when starting for the first time run

```sh
$ docker-compose exec fastapi alembic upgrade head
```

alternatively, for development mode run

```sh
$ docker-compose up -d db
$ uvicorn app.main:app --reload
```

## Access the endpoints

Access API endpoints under

```sh
http://localhost:8000/docs
```