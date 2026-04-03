from pathlib import Path


WEBAPP_DIR = Path(__file__).resolve().parent
REPO_ROOT = WEBAPP_DIR.parent
MODEL_DIR = REPO_ROOT / "model"
INSTANCE_DIR = REPO_ROOT / "instance"
STORAGE_DIR = REPO_ROOT / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
CALIBRATION_DIR = REPO_ROOT / "calibration"
CALIBRATION_ARTIFACTS_DIR = CALIBRATION_DIR / "artifacts"
DEFAULT_DB_PATH = INSTANCE_DIR / "song_eval.sqlite3"
SCORING_WEIGHTS_PATH = WEBAPP_DIR / "config" / "scoring_weights.json"
