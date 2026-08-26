"""The reusable Temporal orchestration kit: contract bases, worker helpers, and the client.

App-agnostic — it defines *how* activities and workflows are dispatched, served, and fail, but names
no specific activity or workflow. Your activities and workflows live outside this package (see
`src/activities/` and `src/workflows/` for the worked examples) and depend on it, never the reverse.
No re-exports; import from the submodule.
"""
