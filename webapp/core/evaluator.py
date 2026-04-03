from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import librosa
import matplotlib.pyplot as plt
import numpy as np
import torch
import torchaudio
from openunmix import utils as openunmix_utils

from webapp.core.scoring import compute_final_score, grade_from_score, load_scoring_weights
from webapp.core.types import EvaluationMetrics, EvaluationResult


TARGET_SAMPLE_RATE = 22_050
FRAME_LENGTH = 2_205
HOP_LENGTH = 512


@dataclass(slots=True)
class PreparedAudio:
    waveform: np.ndarray
    sample_rate: int


class AudioEvaluator:
    def __init__(
        self,
        separator: Any,
        scoring_weights: dict[str, float] | None = None,
        target_sample_rate: int = TARGET_SAMPLE_RATE,
    ) -> None:
        self.separator = separator
        self.scoring_weights = scoring_weights or load_scoring_weights()
        self.target_sample_rate = target_sample_rate

    def evaluate(self, user_audio_path: Path | str, original_audio_path: Path | str, song_name: str) -> EvaluationResult:
        user_audio = self._prepare_audio(Path(user_audio_path))
        original_audio = self._prepare_audio(Path(original_audio_path))

        user_frames = self._frames(user_audio.waveform)
        original_frames = self._frames(original_audio.waveform)

        user_mfccs = self._mfcc_features(user_frames, user_audio.sample_rate)
        original_mfccs = self._mfcc_features(original_frames, original_audio.sample_rate)
        mfcc_error, mfcc_alignment = self._dtw_mean_distance(user_mfccs, original_mfccs)

        user_energy = self._short_term_log_energy(user_frames)
        original_energy = self._short_term_log_energy(original_frames)
        energy_error, energy_alignment = self._dtw_mean_distance(user_energy[:, None], original_energy[:, None])

        user_delta_pitch, user_median_pitch = self._pitch_features(user_frames, user_audio.sample_rate)
        original_delta_pitch, original_median_pitch = self._pitch_features(original_frames, original_audio.sample_rate)
        delta_pitch_error, delta_pitch_alignment = self._dtw_mean_distance(user_delta_pitch[:, None], original_delta_pitch[:, None])
        median_pitch_error, median_pitch_alignment = self._dtw_mean_distance(
            user_median_pitch[:, None],
            original_median_pitch[:, None],
        )

        rop_error = float(
            abs(
                self._range_of_pitch(original_frames, original_audio.sample_rate)
                - self._range_of_pitch(user_frames, user_audio.sample_rate)
            )
        )
        singing_power_ratio = float(
            abs(
                self._singing_power_ratio(original_audio.waveform, original_audio.sample_rate)
                - self._singing_power_ratio(user_audio.waveform, user_audio.sample_rate)
            )
        )

        metrics = EvaluationMetrics(
            mfcc_error=mfcc_error,
            energy_error=energy_error,
            rop_error=rop_error,
            singing_power_ratio=singing_power_ratio,
            delta_pitch_error=delta_pitch_error,
            median_pitch_error=median_pitch_error,
        )

        final_score = compute_final_score(metrics, self.scoring_weights)
        figures = {
            "audio_signal": self._build_audio_figure(user_audio.waveform, original_audio.waveform),
            "pitch_features": self._build_pitch_figure(
                user_delta_pitch,
                original_delta_pitch,
                user_median_pitch,
                original_median_pitch,
            ),
        }
        alignment_metadata = {
            "mfcc": mfcc_alignment,
            "energy": energy_alignment,
            "delta_pitch": delta_pitch_alignment,
            "median_pitch": median_pitch_alignment,
        }

        return EvaluationResult(
            final_score=float(final_score),
            grade=grade_from_score(final_score),
            metrics=metrics,
            figures=figures,
            alignment_metadata=alignment_metadata,
            song_name=song_name,
            evaluated_at=datetime.utcnow(),
        )

    def _prepare_audio(self, audio_path: Path) -> PreparedAudio:
        waveform, sample_rate = torchaudio.load(str(audio_path))
        isolated = self._extract_vocals(waveform, sample_rate)
        trimmed, _ = librosa.effects.trim(isolated)
        if trimmed.size == 0:
            trimmed = isolated
        resampled = librosa.resample(y=trimmed, orig_sr=sample_rate, target_sr=self.target_sample_rate)
        clipped = resampled[: round(3.5 * self.target_sample_rate)]
        if clipped.size < FRAME_LENGTH:
            clipped = np.pad(clipped, (0, FRAME_LENGTH - clipped.size))
        return PreparedAudio(waveform=clipped, sample_rate=self.target_sample_rate)

    def _extract_vocals(self, waveform: torch.Tensor, sample_rate: int) -> np.ndarray:
        model_input = openunmix_utils.preprocess(waveform, rate=sample_rate, model_rate=sample_rate)
        separated = self.separator(model_input)

        vocals: Any = separated
        if isinstance(separated, dict):
            vocals = separated["vocals"]
        elif isinstance(separated, (list, tuple)) and separated:
            vocals = separated[0]

        if hasattr(vocals, "detach"):
            vocals = vocals.detach().cpu().numpy()
        else:
            vocals = np.asarray(vocals)

        vocals = np.squeeze(vocals)
        if vocals.ndim > 1:
            vocals = np.mean(vocals, axis=0)
        return np.asarray(vocals, dtype=np.float32)

    def _frames(self, audio: np.ndarray) -> np.ndarray:
        frames = librosa.util.frame(audio, frame_length=FRAME_LENGTH, hop_length=HOP_LENGTH)
        return np.transpose(frames)

    def _pitch_detection(self, frame: np.ndarray, sample_rate: int) -> np.ndarray:
        pitches, magnitudes = librosa.core.piptrack(y=frame, sr=sample_rate)
        max_indexes = np.argmax(magnitudes, axis=0)
        return pitches[max_indexes, np.arange(magnitudes.shape[1])]

    def _pitch_features(self, frames: np.ndarray, sample_rate: int) -> tuple[np.ndarray, np.ndarray]:
        l2_norms = []
        centered_pitch_norms = []
        for frame in frames:
            pitch_vector = self._pitch_detection(frame, sample_rate)
            l2_norms.append(float(np.linalg.norm(pitch_vector, ord=2)))
            median = np.median(pitch_vector)
            centered_pitch_norms.append(float(np.linalg.norm(pitch_vector - median, ord=2)))

        l2_series = np.asarray(l2_norms, dtype=np.float32)
        delta_pitch = np.nan_to_num(np.diff(l2_series, prepend=l2_series[:1]), nan=0.0)
        return delta_pitch, np.asarray(centered_pitch_norms, dtype=np.float32)

    def _mfcc_features(self, frames: np.ndarray, sample_rate: int) -> np.ndarray:
        features = []
        for frame in frames:
            mfcc = librosa.feature.mfcc(y=frame, sr=sample_rate, n_mfcc=13, hop_length=220, n_fft=2048)
            features.append(np.mean(mfcc, axis=1))
        return np.asarray(features, dtype=np.float32)

    def _short_term_log_energy(self, frames: np.ndarray) -> np.ndarray:
        energy = np.sum(frames**2, axis=1)
        return np.log(np.clip(energy, a_min=1e-8, a_max=None))

    def _range_of_pitch(self, frames: np.ndarray, sample_rate: int) -> float:
        pitch_norms = []
        for frame in frames:
            pitch_vector = self._pitch_detection(frame, sample_rate)
            pitch_norms.append(float(np.linalg.norm(pitch_vector, ord=2)))
        if not pitch_norms:
            return 0.0
        norm_array = np.asarray(pitch_norms, dtype=np.float32)
        return float(norm_array.max() - norm_array.min())

    def _calculate_intensity(self, audio_data: np.ndarray, sample_rate: int, window_func: str = "hann") -> np.ndarray:
        normalized = librosa.util.normalize(audio_data)
        stft = librosa.stft(normalized, window=window_func)
        return librosa.power_to_db(np.abs(stft) ** 2, ref=np.max(np.abs(stft)))

    def _find_peak_intensity(self, intensity_db: np.ndarray, lower_freq: int, higher_freq: int, sample_rate: int) -> float:
        nyquist = sample_rate / 2
        min_idx = int(lower_freq / nyquist * len(intensity_db))
        max_idx = int(higher_freq / nyquist * len(intensity_db))
        band = intensity_db[min_idx:max_idx]
        if band.size == 0:
            return 0.0
        return float(np.max(band))

    def _singing_power_ratio(self, audio_data: np.ndarray, sample_rate: int) -> float:
        intensity_db = self._calculate_intensity(audio_data, sample_rate)
        low_intensity_db = self._find_peak_intensity(intensity_db, 0, 2000, sample_rate)
        high_intensity_db = self._find_peak_intensity(intensity_db, 2000, 4000, sample_rate)
        low_energy = np.exp(low_intensity_db / 10)
        high_energy = np.exp(high_intensity_db / 10)
        if high_energy <= 0:
            return 0.0
        return float(10 * np.log10(low_energy / high_energy))

    def _dtw_mean_distance(self, user_sequence: np.ndarray, original_sequence: np.ndarray) -> tuple[float, dict[str, int]]:
        user_array = self._sanitize_sequence(user_sequence)
        original_array = self._sanitize_sequence(original_sequence)

        if user_array.size == 0 or original_array.size == 0:
            return 0.0, {
                "user_length": int(len(user_array)),
                "original_length": int(len(original_array)),
                "path_length": 0,
            }

        _, warp_path = librosa.sequence.dtw(X=user_array.T, Y=original_array.T, metric="euclidean")
        aligned_user = user_array[warp_path[:, 0]]
        aligned_original = original_array[warp_path[:, 1]]
        distances = np.linalg.norm(aligned_user - aligned_original, axis=1)
        return float(np.mean(distances)), {
            "user_length": int(user_array.shape[0]),
            "original_length": int(original_array.shape[0]),
            "path_length": int(warp_path.shape[0]),
        }

    def _sanitize_sequence(self, sequence: np.ndarray) -> np.ndarray:
        array = np.asarray(sequence, dtype=np.float32)
        if array.ndim == 1:
            array = array[:, None]
        return np.nan_to_num(array, nan=0.0, posinf=0.0, neginf=0.0)

    def _build_audio_figure(self, user_audio: np.ndarray, original_audio: np.ndarray):
        figure, axes = plt.subplots(1, 2, figsize=(14, 4))
        figure.suptitle("Audio Signal Comparison")
        axes[0].plot(user_audio)
        axes[0].set_title("User vocals")
        axes[1].plot(original_audio)
        axes[1].set_title("Reference vocals")
        figure.tight_layout()
        return figure

    def _build_pitch_figure(
        self,
        user_delta_pitch: np.ndarray,
        original_delta_pitch: np.ndarray,
        user_median_pitch: np.ndarray,
        original_median_pitch: np.ndarray,
    ):
        figure, axes = plt.subplots(1, 2, figsize=(14, 5))
        figure.suptitle("Pitch Features")
        axes[0].plot(user_delta_pitch, color="red", label="User delta pitch")
        axes[0].plot(original_delta_pitch, label="Reference delta pitch")
        axes[0].legend()
        axes[0].set_title("Delta pitch")
        axes[1].plot(user_median_pitch, color="red", label="User median pitch")
        axes[1].plot(original_median_pitch, label="Reference median pitch")
        axes[1].legend()
        axes[1].set_title("Median-normalized pitch")
        figure.tight_layout()
        return figure
