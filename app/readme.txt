docker compose exec api alembic revision --autogenerate -m "update users table"

docker compose exec api alembic upgrade head