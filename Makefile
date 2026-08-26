.PHONY: check

check:
	@printf '%s\n' '==> basedpyright'; \
	uv run basedpyright && \
	printf '\n%s\n' '==> ruff' && \
	uv run --only-group dev ruff check && \
	uv run --only-group dev ruff format --check --diff
