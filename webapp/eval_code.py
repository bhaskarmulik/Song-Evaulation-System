import os

import librosa
import matplotlib.pyplot as plt
import numpy as np
import openunmix.predict
import pandas as pd
import scipy
import torch
import torchaudio
import torchaudio.transforms
from openunmix import predict
from openunmix.utils import load_separator


class AudioEval:
    def __init__(self):
        self.use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda" if self.use_cuda else "cpu")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "..", "model")
        self.separator = load_separator(
            model_path,
            targets=["vocals"],
            device=self.device,
            residual=True,
        )

    def trim_audio(self, audio):
        return librosa.effects.trim(audio)[0]

    def resample_audio(self, audio, sr, target_sr):
        return librosa.resample(y=audio, orig_sr=sr, target_sr=target_sr)

    def subset_audio(self, audio, sr):
        return audio[0 : round(3.5 * sr)]

    def frames(self, audio):
        frame_length = 2205
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=512)
        return np.transpose(frames)

    def l2_norm(self, vector):
        return np.linalg.norm(vector, ord=2)

    def pitch_detection(self, y, sr):
        pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
        max_indexes = np.argmax(magnitudes, axis=0)
        pitches = pitches[max_indexes, range(magnitudes.shape[1])]
        return pitches

    def med_sub_p(self, pitch_vector):
        median = np.median(pitch_vector)
        return pitch_vector - median

    def pitch_features(self, frames, sr):
        l2n = []
        pmed = []
        for frame in frames:
            pitch_vector = self.pitch_detection(frame, sr)
            l2n.append(self.l2_norm(pitch_vector))
            medsubp = self.med_sub_p(pitch_vector)
            pmed.append(self.l2_norm(medsubp))
        l2n = pd.Series(l2n)
        pitch_der = l2n.diff()
        return np.array(pitch_der).reshape(-1, 1), np.array(pmed).reshape(-1, 1)

    def mfcc_features(self, frames, sr):
        mfccs = []
        for frame in frames:
            mfcc = librosa.feature.mfcc(y=frame, sr=sr, n_mfcc=13, hop_length=220, n_fft=2048)
            mfccs.append(mfcc)
        return np.array(mfccs)

    def mfcc_err(self, user_mfccs, og_mfccs):
        error = user_mfccs - og_mfccs
        return float(np.mean(error**2))

    def rop(self, user_frames, sr):
        l2n = []
        for frame in user_frames:
            pitch_vector = self.pitch_detection(frame, sr)
            l2n.append(self.l2_norm(pitch_vector))
        l2n = np.array(l2n)
        return l2n.max() - l2n.min()

    def short_term_log_energy(self, frames):
        energy = []
        for frame in frames:
            energy.append(np.log(np.sum(frame**2)))
        return np.array(energy)

    def energy_err(self, user_frames, og_frames):
        user_energy = self.short_term_log_energy(user_frames)
        og_energy = self.short_term_log_energy(og_frames)
        return (user_energy - og_energy).sum()

    def calculate_intensity(self, audio_data, sample_rate, window_func="hann"):
        audio_data = librosa.util.normalize(audio_data)
        stft = librosa.stft(audio_data, window=window_func)
        intensity_db = librosa.power_to_db(np.abs(stft) ** 2, ref=np.max(np.abs(stft)))
        return intensity_db

    def find_peak_intensity(self, intensity_db, lower_freq, higher_freq, sample_rate):
        nyquist = sample_rate / 2
        min_idx = int(lower_freq / nyquist * len(intensity_db))
        max_idx = int(higher_freq / nyquist * len(intensity_db))
        return np.max(intensity_db[min_idx:max_idx])

    def singing_power_ratio(self, audio_data, sample_rate):
        intensity_db = self.calculate_intensity(audio_data, sample_rate)
        low_intensity_db = self.find_peak_intensity(intensity_db, 0, 2000, sample_rate)
        high_intensity_db = self.find_peak_intensity(intensity_db, 2000, 4000, sample_rate)

        if high_intensity_db == np.inf:
            return float("inf")
        return 10 * np.log10(np.exp(low_intensity_db / 10) / np.exp(high_intensity_db / 10))

    def pitch_err(self, user_pitch_f, og_pitch_f):
        vec1 = user_pitch_f[~np.isnan(user_pitch_f)]
        vec2 = og_pitch_f[~np.isnan(og_pitch_f)]
        min_len = min(vec1.shape[0], vec2.shape[0])
        if min_len == 0:
            return 0.0
        return np.abs(vec1[:min_len] - vec2[:min_len]).mean()

    def final_merge(self, uploaded_file, original_file):
        user_song, sr1 = torchaudio.load(uploaded_file)
        original_song, sr2 = torchaudio.load(original_file)

        user_audio = openunmix.utils.preprocess(user_song, rate=sr1, model_rate=sr1)
        og_audio = openunmix.utils.preprocess(original_song, rate=sr2, model_rate=sr2)

        user_audio = self.separator(user_audio)[0][0][0].reshape(-1, 1).T
        og_audio = self.separator(og_audio)[0][0][0].reshape(-1, 1).T

        user_audio = user_audio.detach().cpu().numpy()[0]
        og_audio = og_audio.detach().cpu().numpy()[0]

        figure_audio, ax = plt.subplots(1, 2, figsize=(20, 5))
        figure_audio.suptitle("Audio Signal Comparison")
        ax[0].plot(user_audio)
        ax[0].set_title("User Audio")
        ax[1].plot(og_audio)
        ax[1].set_title("Original Audio")

        user_audio = self.trim_audio(user_audio)
        og_audio = self.trim_audio(og_audio)

        user_audio = self.resample_audio(user_audio, sr1, 22050)
        sr1 = 22050
        og_audio = self.resample_audio(og_audio, sr2, 22050)
        sr2 = 22050

        user_audio = self.subset_audio(user_audio, 22050)
        og_audio = self.subset_audio(og_audio, 22050)

        user_frames = self.frames(user_audio)
        og_frames = self.frames(og_audio)

        user_mfccs = self.mfcc_features(user_frames, sr1)
        og_mfccs = self.mfcc_features(og_frames, sr2)

        mfcc_errors = self.mfcc_err(user_mfccs, og_mfccs)
        rop_err = self.rop(og_frames, sr2) - self.rop(user_frames, sr1)
        energy_errors = self.energy_err(user_frames, og_frames)

        ratio = self.singing_power_ratio(og_audio, sr1)

        user_delta_p, user_pmed = self.pitch_features(user_frames, sr1)
        og_delta_p, og_pmed = self.pitch_features(og_frames, sr2)
        pitch_error1 = self.pitch_err(user_delta_p, og_delta_p)
        pitch_error2 = self.pitch_err(user_pmed, og_pmed)

        figure_pitch, axes = plt.subplots(1, 2, figsize=(20, 10))
        figure_pitch.suptitle("Pitch Features")
        axes[0].plot(user_delta_p, color="red")
        axes[0].set_title("User Audio Delta Pitch vs Og Audio Delta Pitch")
        axes[0].plot(og_delta_p)
        axes[1].plot(user_pmed)
        axes[1].set_title("User Audio Median Pitch vs Og Audio Median Pitch")
        axes[1].plot(og_pmed)
        axes[1].set_title("Original Audio Median Pitch")

        final_err = (
            0.003 * mfcc_errors
            + 0.002 * energy_errors
            + 0.001 * rop_err
            + 0.14 * ratio
            + 1.1 * pitch_error1
            + pitch_error2
        )

        return {
            "final_error": float(final_err),
            "figure_audio": figure_audio,
            "figure_pitch": figure_pitch,
            "metrics": {
                "mfcc_error": float(mfcc_errors),
                "energy_error": float(energy_errors),
                "rop_error": float(rop_err),
                "singing_power_ratio": float(ratio),
                "delta_pitch_error": float(pitch_error1),
                "median_pitch_error": float(pitch_error2),
            },
        }
