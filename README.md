# temporal-py

A reference template for structuring a **Temporal (Python)** orchestration layer. It encodes one
opinion: keep the seam between *deciding what to run* (workflows) and *doing the work* (activities)
import-light and per-unit, so each worker runs in its own minimal image and no unit's dependencies
leak into another's.

Clone it, keep `src/orchestration/`, replace the `example` domain and the `example_*` units with your
own, and you have a working, type-checked, testable skeleton.

## Layout

```
src/
  primitives.py              # FrozenBaseModel, NonEmptyStr, NOT_GIVEN/was_given — no Temporal import
  orchestration/             # THE REUSABLE KIT — app-agnostic; copy this into any repo
    contracts.py             # ActivityContract / WorkflowContract bases
    worker.py                # build_activity_worker / build_workflow_worker
    client.py                # build_client — the Temporal client (hardcoded local target here)
  example/                   # YOUR domain / impl code (worked example) — no Temporal dependency
    models.py                #   domain models, imported by the contracts, definitions, and workflow
    service.py               #   a domain service (a port + an implementation + its factory)
  activities/                # Temporal adapters over the domain — one directory per activity
    names.py                 # ActivityName — the closed, typed set of activity names
    example_plan/
      contract.py            #   the import-light dispatch seam (workflows import this)
      definition.py          #   the @activity.defn wrapping the domain code
      worker.py              #   build_worker(client) -> Worker — this activity's construction
      serve.py               #   the entrypoint: build the client, build the worker, run it
    example_process/         # a second activity, injecting the domain service
  workflows/                 # Temporal adapters — one directory per workflow
    names.py                 # WorkflowName
    example_job/             # same four-module layout as an activity
      { contract, definition, worker, serve }.py
tests/
```

The example workflow (`example_job`) plans two items, fans them out to `example_process`, and reports
the count — enough to exercise the whole path end to end.

## The three areas

- **`src/orchestration/` — the kit.** App-agnostic: it defines *how* activities and workflows are
  dispatched (contracts), served (worker helpers), and connected (client). It names no specific
  activity or workflow. You reuse it verbatim.
- **`src/example/` — the domain.** Your models and business logic, with no dependency on Temporal or
  the kit. In a real app this is many packages; here it's one.
- **`src/activities/`, `src/workflows/` — the adapters.** Thin Temporal wrappers over the domain.
  They depend on the domain and the kit; neither depends on them.

## Key decisions

These are the load-bearing choices. Change them only deliberately.

1. **Contract and definition are separate modules.** The *contract* (`contract.py`) is the
   import-light seam a workflow imports to dispatch by string name — it carries the name, the
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
   domain; the dependency flows one way. So `definition.py` is a thin wrapper — it imports the domain
   service and calls it — and the domain stays testable without Temporal.

4. **`__init__.py` files are empty — no re-exports.** If a package `__init__` re-exported its
   submodules, importing any submodule (even a light contract) would first run the `__init__` and
   pull in its heavy siblings — reintroducing the coupling (2) removes. Import from the full submodule
   path. This makes "importing a contract stays light" a property of the module graph, not luck.
   `src/__init__.py` is also side-effect-free (nothing runs at import).

5. **Payloads are references, not blobs.** Boundary types carry ids / hashes / keys / coordinates,
   never large content, and import nothing heavy. If importing a boundary type would pull a heavy
   dependency, pass a reference and re-derive the heavy view on the worker instead.

6. **No central registry, no "serve everything".** Each image runs its own `serve.py`, which connects
   the client, builds exactly one worker, and runs it. A central `match name -> Worker` that built
   every worker would register nothing and, in one process, would co-import conflicting environments.

7. **Construction lives in each unit's `worker.py`,** over the shared `build_*_worker` helpers, which
   apply the cross-cutting Temporal wiring uniformly. It is *not* on the contract — the contract is
   workflow-facing and stays pure dispatch.

8. **Determinism.** Workflow code (`definition.py`) stays pure and import-light — it imports contracts
   and calls activities by name, never an implementation; use `workflow.now` / `workflow.random` /
   `workflow.uuid4` for time and randomness. Workflows run under Temporal's sandbox (on by default).
   If importing your app package under the sandbox ever trips on an import-time side effect (e.g.
   logging setup that touches `random`), give the workflow worker a `SandboxedWorkflowRunner` that
   passes *only* that module through, keeping the definitions themselves sandboxed.

## Running it

Requires [uv](https://docs.astral.sh/uv/) and Python 3.14.

```bash
uv sync       # create the environment
make check    # basedpyright + ruff (lint + format)
uv run pytest # runs the suite; the end-to-end test starts Temporal's in-memory test server
```

Run each worker against a local dev server (`temporal server start-dev`), each in its own process:

```bash
uv run python -m src.workflows.example_job.serve
uv run python -m src.activities.example_plan.serve
uv run python -m src.activities.example_process.serve
```

Then start a run from a client (`EXAMPLE_JOB_WORKFLOW.start(client, ExampleRequest(...))`); the
workflow id is derived from the payload by the contract's `key`.

## Adding an activity

1. Put its types and logic in your domain (`src/example/` here): the model(s) in `models.py`, any
   service in `service.py`.
2. Add a member to `src/activities/names.py`.
3. Create `src/activities/<activity>/` with:
   - `contract.py` — an `ActivityContract` instance over the domain types;
   - `definition.py` — the `@activity.defn`, importing the domain code;
   - `worker.py` — `build_worker(client)` over `build_activity_worker`;
   - `serve.py` — the `python -m …serve` entrypoint: `build_client()`, `build_worker(client)`, run.
4. Dispatch it from a workflow via its contract's `execute`.

Adding a workflow is the same shape under `src/workflows/`, dispatching activities by contract.

## Not included (deliberately)

- **A completeness lint** — a check that every `ActivityName` / `WorkflowName` has a directory with
  the expected modules, and no orphan directories. Recommended once you have more than a handful of
  units; it makes "no declared name goes unserved" a static guarantee.
- **A failure model, retries-by-policy, observability, persistence** — application concerns to layer
  on top. (An activity interceptor is the natural place for a cross-cutting failure seam if you want
  one.)
- **CI, Dockerfiles, IaC, and worker auth** — deployment concerns. The pattern is one image per
  `serve.py`; wire it to your platform.
