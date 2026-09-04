# temporal-py

A reference template for structuring a **Temporal (Python)** orchestration layer. It follows one
rule: keep the boundary between *deciding what to run* (workflows) and *doing the work* (activities)
import-light and per-unit, so each worker runs in its own minimal image and no unit's dependencies
leak into another's.

Clone it, keep `src/orchestration/`, replace the `example` domain and the `example_*` units with your
own, and you have a working, type-checked, testable skeleton.

## Layout

```
src/
  primitives.py              # FrozenBaseModel, NonEmptyStr, NOT_GIVEN/was_given (no Temporal import)
  example/                   # YOUR domain / impl code (worked example); no Temporal dependency
    models.py                #   domain models, imported by the contracts, definitions, and workflow
    plan.py                  #   a plain domain function (build_plan) the plan activity wraps
    ports.py                 #   the service port (a Protocol)
    service.py               #   a concrete implementation of the port, plus its factory
  orchestration/             # THE TEMPORAL LAYER
    worker-base.Dockerfile   # shared build base for every worker image
    contracts.py             # ActivityContract / WorkflowContract bases (reused as-is)
    converter.py             # typed payload conversion; malformed payloads fail without retrying
    worker.py                # build_activity_worker / build_workflow_worker
    client.py                # build_client: Temporal connection settings and client construction
    activities/              # one directory per activity, each an adapter over the domain
      names.py               #   ActivityName: the closed, typed set of activity names
      example_plan/
        Dockerfile           #     this activity's deployable image
        contract.py          #     the import-light dispatch interface (workflows import this)
        definition.py        #     the @activity.defn wrapping the domain code
        worker.py            #     build_worker(client) -> Worker: this activity's construction
        serve.py             #     the entrypoint: build the client, build the worker, run it
      example_process/       #   a second activity, injecting the domain service
    workflows/               # one directory per workflow
      names.py               #   WorkflowName
      example_job/           #   same four-module layout as an activity
        Dockerfile
        { contract, definition, worker, serve }.py
tests/
compose.yaml                 # local Temporal server and all worker containers
docker-bake.hcl              # authoritative build graph for every worker image
```

The example workflow (`example_job`) plans two items, fans them out to `example_process`, and reports
the count. That exercises the whole path end to end.

## The two sides

- **`src/example/`: the domain.** Your models and business logic, with no dependency on Temporal. In
  a real app this is many packages; here it's one.
- **`src/orchestration/`: the Temporal layer.** The reusable base (`contracts.py`, `worker.py`,
  `client.py`), plus one directory per unit under `activities/` and `workflows/`. Those are thin
  adapters that wrap the domain. Orchestration depends on the domain, never the reverse.

## Key decisions

1. **Contract and definition are separate modules.** The *contract* (`contract.py`) is the
   import-light interface a workflow imports to dispatch by string name: it carries the name, the
   argument/result types, the derived task queue, and the typed `execute` / `start` /
   `execute_as_child` methods. The *definition* (`definition.py`) is the `@activity.defn` and imports
   the real (often heavy) work. Keeping them apart lets a workflow import a contract without dragging
   in the implementation, and keeps the workflow worker's image free of a stage's dependencies.

2. **One directory per activity/workflow.** A worker image imports only the directory it serves, so
   no unit's dependencies meet another's. A single shared `definitions.py` would defeat this:
   importing it runs *all* its top-level imports (naming one symbol imports the whole module), so
   every unit's dependencies load at once.

3. **Domain code lives in the domain, imported by the adapters.** Models and services live in
   `src/example/` (your domain), not inside the Temporal adapters. The adapters import from the
   domain, so the dependency flows one way. `definition.py` is a thin wrapper: it imports the domain
   service and calls it, and the domain stays testable without Temporal.

4. **`__init__.py` files are empty, with no re-exports.** If a package `__init__` re-exported its
   submodules, importing any submodule (even a light contract) would first run the `__init__` and
   pull in its heavy siblings, reintroducing the coupling that (2) removes. Import from the full
   submodule path. This makes "importing a contract stays light" a property of the module graph
   rather than luck. `src/__init__.py` is also side-effect-free (nothing runs at import).

5. **Payloads are references, not blobs.** Boundary types carry ids, hashes, keys, or coordinates,
   never large content, and import nothing heavy. If importing a boundary type would pull a heavy
   dependency, pass a reference and re-derive the heavy view on the worker instead.

6. **No central registry, no "serve everything".** Each image runs its own `serve.py`, which connects
   the client, builds exactly one worker, and runs it. A central `match name -> Worker` that built
   every worker would register nothing and, in one process, would co-import conflicting environments.

7. **Construction lives in each unit's `worker.py`,** over the shared `build_*_worker` helpers, which
   apply the cross-cutting Temporal wiring uniformly. It does not belong on the contract: the contract
   is workflow-facing and stays pure dispatch.

8. **Determinism.** Workflow code (`definition.py`) stays pure and import-light: it imports contracts
   and calls activities by name, never an implementation, and uses `workflow.now` / `workflow.random`
   / `workflow.uuid4` for time and randomness. Workflows run under Temporal's sandbox (on by default).
   If importing your app package under the sandbox ever trips on an import-time side effect (say,
   logging setup that touches `random`), give the workflow worker a `SandboxedWorkflowRunner` that
   passes only that module through, keeping the definitions themselves sandboxed.

9. **Malformed typed payloads are terminal failures.** The data converter translates Pydantic
   `ValidationError` failures for activity and workflow inputs and outputs into non-retryable Temporal
   `ApplicationError` failures. Retrying the same malformed payload cannot succeed, so workers fail
   it immediately rather than repeatedly executing a deterministic validation failure.

## Running it

Requires [uv](https://docs.astral.sh/uv/) and Python 3.14.

```bash
uv sync       # create the environment with dev and every worker dependency group
make check    # basedpyright + ruff (lint + format)
uv run pytest # runs the suite; the end-to-end test starts Temporal's in-memory test server
```

Run each worker against a local dev server (`temporal server start-dev`), each in its own process:

```bash
uv run python -m src.orchestration.workflows.example_job.serve
uv run python -m src.orchestration.activities.example_plan.serve
uv run python -m src.orchestration.activities.example_process.serve
```

Then start a run from a client (`EXAMPLE_JOB_WORKFLOW.start(client, ExampleRequest(...))`); the
workflow id is derived from the payload by the contract's `key`.

`build_client()` reads `TEMPORAL_TARGET` and `TEMPORAL_NAMESPACE`, defaulting to
`localhost:7233` and `default` for native local development.

## Container images

Each activity and workflow owns a Dockerfile beside its `serve.py`. Those images inherit from
`src/orchestration/worker-base.Dockerfile`, which contains Python, uv, and only the dependencies
shared by every worker. The base is internal to the Bake graph: it is built when needed but is not
tagged or published as a deployable image.

The example activities use separate representative dependency groups:

- `example_plan` selects `activity-example-plan`, containing `networkx`;
- `example_process` selects `activity-example-process`, containing `httpx`;
- `example_job` selects neither activity group.

The root `uv.lock` contains the union of these compatible dependencies. Plain `uv sync` installs
all groups for convenient local development, while each Dockerfile selects only its own group. The
final build step runs `uv pip check` against the installed image environment.

Build and load every deployable image into the local Docker engine:

```bash
make images
```

Build one image by naming its Bake target, for example:

```bash
docker buildx bake --load example-plan
```

`IMAGE_PREFIX` and `IMAGE_TAG` default to `temporal-py` and `local`; set both consistently when
using different local image names.

## Containerized local development

Build the images, then start a Temporal development server and every worker container:

```bash
make compose-up
```

Compose only runs the images produced by Bake; it does not define or trigger their builds. Workers
connect to `temporal:7233` inside the Compose network. Clients on the host connect to
`localhost:7233`, and the Temporal UI is available at <http://localhost:8233>. Compose starts
workers but does not start a workflow, so expensive or side-effecting runs remain deliberate.

Stop the stack while keeping its local Temporal data:

```bash
make compose-down
```

Run `docker compose down --volumes` when that development history should also be discarded.

## Adding an activity

1. Put its types and logic in your domain (`src/example/` here): the model(s) in `models.py`, any
   service in `service.py`.
2. Add a member to `src/orchestration/activities/names.py`.
3. Create `src/orchestration/activities/<activity>/` with:
   - `Dockerfile`: the activity image, selecting only this activity's dependency group;
   - `contract.py`: an `ActivityContract` instance over the domain types;
   - `definition.py`: the `@activity.defn`, importing the domain code;
   - `worker.py`: `build_worker(client)` over `build_activity_worker`;
   - `serve.py`: the `python -m …serve` entrypoint (`build_client()`, `build_worker(client)`, run).
4. If it has unique dependencies, add them with `uv add --group activity-<activity> <package>`.
5. Add its image target to `docker-bake.hcl` and its runtime service to `compose.yaml`.
6. Dispatch it from a workflow via its contract's `execute`.

Adding a workflow is the same shape under `src/orchestration/workflows/`, dispatching activities by
contract.

## Not included (deliberately)

- **A completeness lint:** a check that every `ActivityName` / `WorkflowName` has a directory with
  the expected modules, and no orphan directories. Worth adding once you have more than a handful of
  units; it makes "no declared name goes unserved" a static guarantee.
- **A domain failure model, retries-by-policy, observability, persistence:** application concerns to
  layer on top. (Malformed Pydantic inputs and outputs are already terminal boundary failures.)
- **CI, registry publishing, Kubernetes manifests, IaC, and worker auth:** later deployment layers.
  The current layer builds one image per `serve.py` and provides a containerized local runtime.
