"""Loading the repo-local ``.env`` file into the process environment."""

from functools import cache

from dotenv import load_dotenv


@cache
def load_env() -> None:
    """Load the repo-local ``.env`` into ``os.environ`` once per process.

    Called at the top of the ``production_*`` factories so locally-run code sees ``.env`` settings
    no matter which entrypoint imported it first. Variables already present are never overridden,
    and a deployed process with no ``.env`` file makes this a no-op.
    """
    load_dotenv()
