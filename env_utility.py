"""env_utility.py

Utility to load a base .env file then an environment-specific .env.{ENV} file
where the latter overrides values from the base .env.

Usage:
    from env_utility import load_env
    env, values = load_env(base_dir=<project_root>)

This implementation does not require python-dotenv and will set os.environ values.
"""

import os
from pathlib import Path


def _strip_quotes(s: str) -> str:
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def _parse_env_file(path: Path) -> dict:
    data = {}
    with path.open('r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip()
            val = _strip_quotes(val)
            data[key] = val
    return data


def _load_file(path: Path, override: bool = False) -> dict:
    parsed = _parse_env_file(path)
    for k, v in parsed.items():
        if override or k not in os.environ:
            os.environ[k] = v
    return parsed


def load_env(base_dir: str | Path | None = None, env_var_name: str = 'ENVIRONMENT') -> tuple[str, dict]:
    """Load .env then .env.{ENV} (where ENV is read from env_var_name) and apply overrides.

    - base_dir: directory containing the .env files (defaults to CWD)
    - env_var_name: the variable name in .env that indicates which environment to load

    Returns (env_name, merged_values_dict) where merged_values_dict contains the final values loaded.
    """
    base = Path(base_dir) if base_dir else Path.cwd()
    primary = base / '.env'
    merged = {}

    if primary.exists():
        merged.update(_load_file(primary, override=False))

    # determine environment name: prefer already-set environment variable, then loaded .env value, then 'development'
    env = os.getenv(env_var_name) or merged.get(env_var_name) or 'development'

    secondary = base / f'.env.{env}'
    if secondary.exists():
        merged.update(_load_file(secondary, override=True))

    # refresh merged values from os.environ for accuracy
    for k in list(merged.keys()):
        merged[k] = os.getenv(k)

    return env, merged


# Convenience getters for common types
def env_get(key: str, default: str | None = None) -> str | None:
    """Retrieve environment variable as string with optional default."""
    return os.getenv(key, default)


def env_bool(key: str, default: bool = False) -> bool:
    """Retrieve environment variable as boolean.

    Interprets '1', 'true', 'yes', 'on' (case-insensitive) as True.
    """
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in ('1', 'true', 'yes', 'on')


def env_int(key: str, default: int = 0) -> int:
    """Retrieve environment variable as integer with fallback to default."""
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def env_list(key: str, separator: str = ',', default: list | None = None) -> list:
    """Retrieve environment variable as list split by separator, trimming whitespace."""
    if default is None:
        default = []
    val = os.getenv(key)
    if not val:
        return default
    return [item.strip() for item in val.split(separator)]
