"""Activities — one directory per activity, each a Temporal adapter over the domain.

`names.py` is the closed set of activity names. Each activity has its own directory
(`<activity>/{contract,definition,worker,serve}.py`), so a worker image imports only the activity it
serves and no unit's dependencies meet another's. The image runs the activity's `serve.py`.
"""
