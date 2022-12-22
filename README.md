# FastAPI + SQLModel + Alembic

FastAPI Auth boilerplate that uses SQLAlchemy, Postgres, Alembic, and Docker.

## Want to use this project?

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
