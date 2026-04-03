from __future__ import annotations

import json
from pathlib import Path

from webapp.app_paths import SCORING_WEIGHTS_PATH
from webapp.core.types import EvaluationMetrics


DEFAULT_WEIGHTS = {
    "mfcc_error": 0.003,
    "energy_error": 0.002,
    "rop_error": 0.001,
    "singing_power_ratio": 0.14,
    "delta_pitch_error": 1.1,
    "median_pitch_error": 1.0,
}

GRADE_BOUNDS = (
    (2000, "A"),
    (6000, "B"),
    (12000, "C"),
    (17000, "D"),
)


def load_scoring_weights(weights_path: Path | None = None) -> dict[str, float]:
    path = weights_path or SCORING_WEIGHTS_PATH
    if not path.exists():
        return DEFAULT_WEIGHTS.copy()

    data = json.loads(path.read_text())
    weights = DEFAULT_WEIGHTS.copy()
    weights.update({key: float(value) for key, value in data.items() if key in DEFAULT_WEIGHTS})
    return weights


def compute_final_score(metrics: EvaluationMetrics, weights: dict[str, float] | None = None) -> float:
    active_weights = weights or load_scoring_weights()
    metric_values = metrics.as_dict()
    return float(sum(active_weights[key] * metric_values[key] for key in DEFAULT_WEIGHTS))


def grade_from_score(score: float) -> str:
    for upper_bound, grade in GRADE_BOUNDS:
        if score < upper_bound:
            return grade
    return "F"
