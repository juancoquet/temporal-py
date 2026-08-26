"""Example domain / implementation code — the "real work" a Temporal activity wraps.

In a real service this is your business logic and its types, with no dependency on Temporal or the
orchestration layer. The activities in `src/activities/` are thin adapters that import from here and
wrap it in `@activity.defn`; the dependency flows one way (activities → this package), never back.
No re-exports.
"""
