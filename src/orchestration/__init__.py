"""The Temporal orchestration layer.

Holds the generic seam — contract bases (`contracts.py`), worker helpers (`worker.py`), the client
(`client.py`) — and, under `activities/` and `workflows/`, one directory per activity/workflow. The
domain code these adapters wrap lives outside, in `src/example/`. No re-exports; import from the
submodule.
"""
