"""Example workflows — the app side of the seam, outside the orchestration kit.

`names.py` is the closed set of workflow names. Each workflow has its own directory
(`<workflow>/{contract,definition,worker,serve}.py`), mirroring the activity side. Workflow code
stays import-light (it imports activity *contracts*, never their definitions). No re-exports.
"""
