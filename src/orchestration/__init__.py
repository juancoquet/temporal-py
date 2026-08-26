"""The Temporal orchestration layer.

Holds the generic contracts (`contracts.py`), worker helpers (`worker.py`), and client
(`client.py`), plus, under `activities/` and `workflows/`, one directory per activity/workflow. The
domain code these adapters wrap lives outside, in `src/example/`. No re-exports; import from the
submodule.
"""
