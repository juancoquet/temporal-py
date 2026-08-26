# temporal-py

A reference template for structuring a **Temporal (Python)** orchestration layer. It encodes one
opinion: keep the seam between *deciding what to run* (workflows) and *doing the work* (activities)
import-light and per-unit, so each worker runs in its own minimal image and no stage's dependencies
leak into another's.

Clone it, keep `src/orchestration/` and `src/primitives.py`, replace the `example_*` units with your
own, and you have a working, type-checked, testable skeleton.

## Layout

```
src/
  primitives.py              # FrozenBaseModel, Id, NonEmptyStr, NOT_GIVEN/was_given, Panic — no Temporal import
  config/
    env.py                   # load the repo-local .env
    temporal.py              # TemporalConfig (endpoint + namespace) read from the environment
  orchestration/             # THE REUSABLE KIT — app-agnostic; copy this into any repo
    contracts.py             # ActivityContract / WorkflowContract bases + WorkflowId
    worker.py                # build_activity_worker / build_workflow_worker (+ the sandbox runner)
    client.py                # the Temporal client builder (pydantic data converter)
    interceptor.py           # PanicInterceptor — the failure seam
  activities/                # YOUR activities (worked examples here)
    names.py                 # ActivityName — the closed, typed set of activity names
    example_plan/            # one directory per activity
      contract.py            #   the import-light dispatch seam (workflows import this)
      definition.py          #   the @activity.defn — the only module that imports the real work
      worker.py              #   build_worker(client) -> Worker — this activity's construction
      serve.py               #   the entrypoint: `python -m src.activities.example_plan.serve`
    example_process/         # a second activity, with a constructor-injected collaborator
  workflows/                 # YOUR workflows (worked example here)
    names.py                 # WorkflowName
    example_job/             # same four-module layout as an activity
      { contract, definition, worker, serve }.py
tests/
```

The example workflow (`example_job`) plans two items, fans them out to `example_process`, and reports
the count — enough to exercise the whole path end to end.

## The two sides

- **`src/orchestration/` — the kit.** App-agnostic: it defines *how* activities and workflows are
  dispatched (contracts), served (worker helpers), connected (client), and how they fail (the Panic
  interceptor). It names no specific activity or workflow. This is the part you reuse verbatim.
- **`src/activities/`, `src/workflows/` — your app.** These depend on the kit; the kit never depends
  on them. Each activity/workflow is a self-contained directory.

## Key decisions

These are the load-bearing choices. Change them only deliberately.

1. **Contract and definition are separate modules.** The *contract* (`contract.py`) is the
   import-light seam a workflow imports to dispatch by string name — it carries the name, the
   argument/result types, the derived task queue, and the typed `execute` / `start` /
   `execute_as_child` methods. The *definition* (`definition.py`) is the `@activity.defn` and imports
   the real (often heavy) work. Keeping them apart is what lets a workflow import a contract without
   dragging in the implementation, and keeps the workflow worker's image free of stage dependencies.

2. **One directory per activity/workflow.** A worker image imports only the directory it serves, so
   no unit's dependencies meet another's. A single shared `definitions.py` would defeat this:
   importing it runs *all* its top-level imports (naming one symbol imports the whole module), so
   every unit's dependencies load at once.

3. **`__init__.py` files are empty — no re-exports.** If a package `__init__` re-exported its
   submodules, importing any submodule (even a light contract) would first run the `__init__` and
   pull in its heavy siblings — reintroducing the coupling (2) removes. Import from the full
   submodule path. This makes "importing a contract stays light" a property of the module graph, not
   luck. (`src/__init__.py` is also side-effect-free for the same reason — see the determinism note.)

4. **Payloads are references, not blobs.** Boundary types carry ids / hashes / keys / coordinates,
   never large content, and must import nothing heavy. If importing a boundary type would pull a
   heavy dependency, pass a reference and re-derive the heavy view on the worker instead.

5. **No central registry, no "serve everything".** Each image runs its own `serve.py`, which builds
   and runs exactly one worker. A central `match name -> Worker` that built every worker would
   register nothing and, run in one process, would co-import conflicting environments. Completeness
   (every declared name has a served worker) is a structural invariant — every unit directory carries
   the four modules — best enforced by a lint (not included; see below).

6. **Construction lives in each unit's `worker.py`,** over the shared `build_*_worker` helpers, which
   apply the cross-cutting wiring uniformly: the `PanicInterceptor` on every activity, the sandboxed
   runner on every workflow. It is *not* on the contract — the contract is workflow-facing and stays
   pure dispatch.

7. **The failure seam.** `Panic` (in `primitives.py`) is a pure-domain *raised* exception with no
   Temporal import at its home. The `PanicInterceptor` maps a raised `Panic` to a non-retryable
   Temporal failure; a returned domain error flows back as a value; a genuine transient propagates
   for Temporal to retry. Task code stays Temporal-agnostic.

8. **Determinism.** Workflow code (`definition.py`) stays pure and import-light — it imports contracts
   and calls activities by name, never an implementation; use `workflow.now` / `workflow.random` /
   `workflow.uuid4` for time and randomness. The workflow sandbox is left on. If importing your app
   package under the sandbox ever trips on an import-time side effect (e.g. logging setup that
   touches `random`), pass *only* that module through in `orchestration/worker.py`, keeping the
   definitions themselves sandboxed.

## Running it

Requires [uv](https://docs.astral.sh/uv/) and Python 3.14.

```bash
uv sync                 # create the environment
make check              # basedpyright + ruff (lint + format)
make test               # the hermetic `small` suite
uv run pytest -m medium # the end-to-end test (starts Temporal's in-memory test server)
```

Run a worker against a local dev server (`temporal server start-dev`), each in its own process:

```bash
uv run python -m src.workflows.example_job.serve
uv run python -m src.activities.example_plan.serve
uv run python -m src.activities.example_process.serve
```

Then start a run from a client (`EXAMPLE_JOB_WORKFLOW.start(client, ExampleRequest(...))`); the
workflow id is derived from the payload by the contract's `key`.

## Adding an activity

1. Add a member to `src/activities/names.py`.
2. Create `src/activities/<activity>/` with:
   - `contract.py` — an `ActivityContract` instance plus its (light, reference-only) boundary types;
   - `definition.py` — the `@activity.defn`, importing your real work;
   - `worker.py` — `build_worker(client)` over `build_activity_worker`;
   - `serve.py` — the `python -m …serve` entrypoint.
3. Dispatch it from a workflow via its contract's `execute`.

Adding a workflow is the same shape under `src/workflows/`, dispatching activities by contract.

## Not included (deliberately)

- **A completeness lint** — a check that every `ActivityName` / `WorkflowName` has a directory with
  the four modules, and no orphan directories. Recommended once you have more than a handful of
  units; it restores, statically, the "no declared name goes unserved" guarantee.
- **CI, Dockerfiles, IaC, and worker auth** — deployment concerns. The pattern is one image per
  `serve.py`; wire it to your platform.
- **Persistence, observability, retries-by-policy** — application concerns layered on top.
