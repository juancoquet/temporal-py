# temporal-py

A reference structure for a typed Temporal Python application. Each workflow and activity has its
own worker and image, so implementation dependencies stay isolated.

Replace the example domain and orchestration units with your own.

## Layout

```text
src/
  primitives.py
  example/                              # Domain models and logic; no Temporal dependency
  orchestration/
    client.py                           # Temporal connection and client construction
    contracts.py                        # Typed activity and workflow dispatch
    converter.py                        # Pydantic payload conversion
    worker.py                           # Shared worker construction
    worker-base.Dockerfile              # Shared worker image base
    activities/
      names.py                           # Closed set of activity names
      example_plan/
        contract.py                      # Import-light dispatch interface
        definition.py                    # Activity definition wrapping domain logic
        worker.py                        # Worker construction
        serve.py                         # Process entrypoint
        Dockerfile                       # Deployable image
      example_process/
    workflows/
      names.py                           # Closed set of workflow names
      example_job/
        contract.py                      # Import-light dispatch interface
        definition.py                    # Workflow definition
        worker.py                        # Worker construction
        serve.py                         # Process entrypoint
        Dockerfile                       # Deployable image
tests/
compose.yaml                            # Local Temporal server and workers
docker-bake.hcl                         # Worker image build graph
```

The example workflow plans two items, processes them in parallel, and reports the count.

## Design

- Domain code does not depend on Temporal. Activities are thin adapters over it.
- Contracts contain the import-light interface used by workflows. Definitions contain the
  implementation and its dependencies.
- Each `serve.py` runs one worker on its own task queue and has a colocated Dockerfile.
- Package `__init__.py` files stay empty to avoid pulling implementations into workflow imports.
- Payloads carry references such as IDs and keys rather than large content.
- Malformed typed payloads become non-retryable Temporal failures.

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.14.

```bash
uv sync
make check
uv run pytest
```

`uv sync` installs the development dependencies and every compatible worker dependency group.

## Containers

The shared base image contains Python, uv, and common dependencies. Each worker image adds only its
own dependency group. Bake builds the base internally and produces the deployable worker images.

Build all images without starting them:

```bash
docker buildx bake --load
```

Build and start Temporal and every worker:

```bash
make compose-up
```

Compose starts workers but does not start a workflow. Temporal is available to host clients at
`localhost:7233`, and its UI is at <http://localhost:8233>.

Stop the stack while retaining local Temporal history:

```bash
make compose-down
```

Remove the history as well with `docker compose down --volumes`.

## Adding an activity

1. Add its models and logic to the domain.
2. Add its name to `src/orchestration/activities/names.py`.
3. Create `src/orchestration/activities/<name>/` with `contract.py`, `definition.py`, `worker.py`,
   `serve.py`, and `Dockerfile`.
4. Add unique dependencies with `uv add --group activity-<name> <package>` and select that group in
   its Dockerfile.
5. Add the image to `docker-bake.hcl` and the worker to `compose.yaml`.
6. Dispatch it from a workflow through its contract.

Workflows use the same structure under `src/orchestration/workflows/`.

## Scope

CI, registry publishing, Kubernetes manifests, infrastructure, worker authentication, observability,
and application-specific retry policies are not included.
