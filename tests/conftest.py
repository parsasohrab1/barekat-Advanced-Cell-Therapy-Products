"""Hermetic test environment: sqlite DB, local storage, scratch model dir (never data/models)."""

import os
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix="barekat-tests-")
os.environ.update(
    {
        "DATABASE_URL": f"sqlite:///{Path(_TMP).as_posix()}/test.db",
        "STORAGE_BACKEND": "local",
        "LOCAL_STORAGE_DIR": f"{Path(_TMP).as_posix()}/uploads",
        "MODEL_PATH": f"{Path(_TMP).as_posix()}/models",
        "AUTH_REQUIRED": "false",
        "DEBUG": "false",
    }
)
