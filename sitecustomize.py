"""
Auto-add project paths to Python import search path.

This ensures `import src` works when running tools from the repo root
without needing to export PYTHONPATH or rely on per-run sys.path tweaks.
"""
import os
import sys

try:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(repo_root, "backend")
    src_dir = os.path.join(backend_dir, "src")

    # Prepend so these take priority over site-packages shims if any
    for p in (backend_dir, src_dir):
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)
except Exception:
    # Never block interpreter startup on path helper issues
    pass

