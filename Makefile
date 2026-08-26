.PHONY: check test

# Type-check, lint, and format-check the whole tree — matches what CI runs.
check:
	@printf '%s\n' '==> basedpyright'; \
	uv run basedpyright && \
	printf '\n%s\n' '==> ruff' && \
	uv run --only-group dev ruff check && \
	uv run --only-group dev ruff format --check --diff

# Run the test suite in parallel. The end-to-end test starts Temporal's in-memory test server
# (a one-time binary fetch on first run).
test:
	uv run pytest -n auto
