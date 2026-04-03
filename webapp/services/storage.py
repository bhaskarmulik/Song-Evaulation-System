from __future__ import annotations

from datetime import datetime
from pathlib import Path

from webapp.app_paths import CALIBRATION_ARTIFACTS_DIR, INSTANCE_DIR, UPLOADS_DIR


def ensure_runtime_directories() -> None:
    for path in (INSTANCE_DIR, UPLOADS_DIR, CALIBRATION_ARTIFACTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    compact = "-".join(part for part in cleaned.split("-") if part)
    return compact or "anonymous"


def persist_uploaded_file(file_obj, user_name: str, label: str) -> Path:
    ensure_runtime_directories()
    extension = Path(file_obj.name).suffix or ".wav"
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    target_dir = UPLOADS_DIR / slugify(user_name)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{timestamp}_{slugify(label)}{extension}"
    target_path.write_bytes(file_obj.getbuffer())
    return target_path
