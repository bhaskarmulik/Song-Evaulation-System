from __future__ import annotations

from pathlib import Path

import torch
from openunmix.utils import load_separator

from webapp.app_paths import MODEL_DIR


WEIGHT_FILENAME = "vocals-b62c91ce.pth"


def load_separator_model(model_dir: Path | None = None):
    active_model_dir = model_dir or MODEL_DIR
    weight_path = active_model_dir / WEIGHT_FILENAME
    if not active_model_dir.exists() or not weight_path.exists():
        raise FileNotFoundError(
            f"OpenUnmix weights not found at {weight_path}. "
            "Run `python3 webapp/scripts/download_openunmix_weights.py` first."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return load_separator(
        str(active_model_dir),
        targets=["vocals"],
        device=device,
        residual=True,
    )
