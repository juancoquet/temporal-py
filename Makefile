.PHONY: check images compose-up compose-down

check:
	@printf '%s\n' '==> basedpyright'; \
	uv run basedpyright && \
	printf '\n%s\n' '==> ruff' && \
	uv run --only-group dev ruff check && \
	uv run --only-group dev ruff format --check --diff

images:
	docker buildx bake --load

compose-up: images
	docker compose up

compose-down:
	docker compose down
