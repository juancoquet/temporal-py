.PHONY: check compose-up compose-down

check:
	@printf '%s\n' '==> basedpyright'; \
	uv run basedpyright && \
	printf '\n%s\n' '==> ruff' && \
	uv run --only-group dev ruff check && \
	uv run --only-group dev ruff format --check --diff

compose-up:
	docker buildx bake --load
	docker compose up

compose-down:
	docker compose down
