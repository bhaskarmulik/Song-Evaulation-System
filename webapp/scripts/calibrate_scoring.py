from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sklearn.linear_model import LinearRegression

from webapp.app_paths import REPO_ROOT, SCORING_WEIGHTS_PATH
from webapp.core import AudioEvaluator
from webapp.services.model_loader import load_separator_model
from webapp.services.storage import ensure_runtime_directories


FEATURE_NAMES = [
    "mfcc_error",
    "energy_error",
    "rop_error",
    "singing_power_ratio",
    "delta_pitch_error",
    "median_pitch_error",
]


def load_manifest(manifest_path: Path) -> list[dict[str, object]]:
    return json.loads(manifest_path.read_text())


def normalize_label(entry: dict[str, object]) -> float:
    if "label_score" in entry:
        return float(entry["label_score"])

    quality_class = str(entry.get("quality_class", "")).strip().lower()
    if quality_class == "perfect":
        return 100.0
    if quality_class == "bad":
        return 0.0
    raise ValueError("Each calibration entry needs either label_score or quality_class.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fit provisional scoring weights from labeled cover examples.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "calibration" / "bootstrap_manifest.json",
        help="JSON file containing provisional calibration examples.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SCORING_WEIGHTS_PATH,
        help="Output JSON file for fitted weights. Defaults to the runtime scoring config.",
    )
    args = parser.parse_args()

    ensure_runtime_directories()
    separator = load_separator_model()
    evaluator = AudioEvaluator(separator=separator)
    rows = load_manifest(args.manifest)

    feature_rows = []
    targets = []
    for row in rows:
        result = evaluator.evaluate(
            user_audio_path=REPO_ROOT / str(row["cover_path"]),
            original_audio_path=REPO_ROOT / str(row["original_path"]),
            song_name=str(row["reference_song"]),
        )
        metrics = result.metrics.as_dict()
        feature_rows.append([metrics[name] for name in FEATURE_NAMES])
        targets.append(normalize_label(row))

    regressor = LinearRegression()
    regressor.fit(feature_rows, targets)

    weights = {name: float(abs(coef)) for name, coef in zip(FEATURE_NAMES, regressor.coef_)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(weights, indent=2))
    print(json.dumps({"weights": weights, "intercept": regressor.intercept_}, indent=2))


if __name__ == "__main__":
    main()
