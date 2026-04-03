from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class EvaluationMetrics:
    mfcc_error: float
    energy_error: float
    rop_error: float
    singing_power_ratio: float
    delta_pitch_error: float
    median_pitch_error: float

    def as_dict(self) -> dict[str, float]:
        return {
            "mfcc_error": self.mfcc_error,
            "energy_error": self.energy_error,
            "rop_error": self.rop_error,
            "singing_power_ratio": self.singing_power_ratio,
            "delta_pitch_error": self.delta_pitch_error,
            "median_pitch_error": self.median_pitch_error,
        }


@dataclass(slots=True)
class EvaluationResult:
    final_score: float
    grade: str
    metrics: EvaluationMetrics
    figures: dict[str, Any]
    alignment_metadata: dict[str, Any]
    song_name: str
    evaluated_at: datetime

    def to_record(self) -> dict[str, Any]:
        return {
            "final_score": self.final_score,
            "grade": self.grade,
            "song_name": self.song_name,
            "evaluated_at": self.evaluated_at.isoformat(),
            "metrics": self.metrics.as_dict(),
            "alignment_metadata": self.alignment_metadata,
        }
