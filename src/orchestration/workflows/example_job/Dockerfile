# syntax=docker/dockerfile:1

FROM worker-base

# The project metadata names README.md, so it is required when uv installs the project.
COPY --chown=app:app README.md ./
COPY --chown=app:app src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-default-groups --no-editable \
    && uv pip check

USER app

CMD ["python", "-m", "src.orchestration.workflows.example_job.serve"]
