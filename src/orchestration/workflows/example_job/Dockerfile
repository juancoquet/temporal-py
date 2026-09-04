# syntax=docker/dockerfile:1

FROM worker-base

COPY --chown=app:app README.md ./
COPY --chown=app:app src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-default-groups --no-editable \
    && uv pip check

USER app

CMD ["python", "-m", "src.orchestration.workflows.example_job.serve"]
