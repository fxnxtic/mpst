all:
	make install
	make run

lint:
	uv run ruff check src --fix
	uv run ruff format src

install:
	uv venv
	uv sync --frozen
	uv run alembic upgrade head

run:
	uv run -m src

migrate:
	@read -p "Enter migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1
