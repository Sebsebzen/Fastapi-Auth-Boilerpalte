# FastAPI + SQLModel + Alembic

FastAPI boilerplate that uses SQLAlchemy, Postgres, Alembic, and Docker.

## Want to use this project?

Add missing environment varialbles to `docker-compose.yaml`

```sh
$ docker-compose up -d --build
$ docker-compose exec fastapi alembic upgrade head
```
