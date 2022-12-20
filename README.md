# FastAPI + SQLModel + Alembic

FastAPI boilerplate that uses SQLAlchemy, Postgres, Alembic, and Docker.

## Want to use this project?

Add missing environment varialbles to `.env` file in `fastapi` folder

```sh
MAILGUN_API_KEY=<mailgun-api-key>
```

then run

```sh
$ docker-compose up -d --build
```

when starting for the first time run

```sh
$ docker-compose exec fastapi alembic upgrade head
```
