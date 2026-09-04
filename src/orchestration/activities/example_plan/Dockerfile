# syntax=docker/dockerfile:1

FROM worker-base

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-default-groups --group activity-example-plan --no-install-project

COPY --chown=app:app README.md ./
COPY --chown=app:app src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-default-groups --group activity-example-plan --no-editable \
    && uv pip check

USER app

CMD ["python", "-m", "src.orchestration.activities.example_plan.serve"]
