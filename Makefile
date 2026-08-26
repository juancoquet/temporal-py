.PHONY: check test

# Type-check, lint, and format-check the whole tree — matches what CI runs.
check:
	@printf '%s\n' '==> basedpyright'; \
	uv run basedpyright && \
	printf '\n%s\n' '==> ruff' && \
	uv run --only-group dev ruff check && \
	uv run --only-group dev ruff format --check --diff

# Run the hermetic test suite in parallel.
test:
	uv run pytest -n auto -m small
