"""Shared helpers: read keys from the environment or a local .env (never printed, never written)."""
import os
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):          # Windows consoles default to cp1252: never crash on a voice name
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def load_env():
    """Fill os.environ from ./.env (cwd) or the skill folder's .env, without overriding real env vars."""
    for p in (Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env"):
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def need(name):
    load_env()
    v = os.environ.get(name, "").strip()
    if not v:
        raise SystemExit(f"Missing {name}. Set it in your environment or in a local .env (see .env.example).")
    return v


def has(name):
    load_env()
    return bool(os.environ.get(name, "").strip())
