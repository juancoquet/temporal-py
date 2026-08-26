"""Workflows — one directory per workflow, mirroring the activity side.

`names.py` is the closed set of workflow names. Workflow code stays import-light (it imports
activity *contracts*, never their definitions). The image runs the workflow's `serve.py`.
"""
