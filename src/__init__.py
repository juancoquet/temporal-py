"""Application package root — intentionally free of import-time side effects.

Keeping this (and every package `__init__`) empty is part of the import-hygiene discipline:
importing a submodule must not run package-level code that drags in unrelated or heavy
dependencies. `__init__` files re-export nothing; consumers import from the full submodule path.
See the README.
"""
