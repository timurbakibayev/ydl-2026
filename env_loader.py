"""Tiny .env loader (stdlib only).

Reads key=value pairs from a .env file in the project root into os.environ,
so the example programs can pull secrets out of .env instead of hardcoding
them. No external dependency (python-dotenv) required.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def load_env(path: str | None = None) -> None:
    """Load key=value pairs from a .env file into os.environ.

    Existing environment variables are not overwritten. Lines that are
    blank or start with '#' are ignored. Missing .env is not an error.
    """
    if path is None:
        path = os.path.join(PROJECT_ROOT, ".env")

    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def require_env(name: str) -> str:
    """Return an env var, raising a clear error if it is missing."""
    load_env()
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name!r} is not set. "
            f"Copy .env.example to .env and fill in the keys."
        )
    return value
