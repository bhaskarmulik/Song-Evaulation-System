# Song Evaluation System

A Streamlit application that compares a singer's uploaded cover against an original song using vocal-source separation and signal-analysis features. The system isolates vocals first, then evaluates similarity using MFCCs, pitch-derived features, short-term energy, and singing power ratio.

## Features

- Vocal extraction with **OpenUnmix** to reduce background instrumentation impact.
- Audio feature comparison using:
  - MFCC error
  - Range of Pitch (RoP) error
  - Short-term log-energy error
  - Singing power ratio
  - Pitch derivative and median-normalized pitch error
- Grade output (A–F) based on combined error score.
- Streamlit multi-page app structure.

## Installation (uv)

This project uses **uv** for dependency and package management.

1. Install uv (if not already installed):
   ```bash
   pip install uv
   ```
2. Create and sync the environment from `pyproject.toml`:
   ```bash
   uv sync
   ```

> Optional: if you prefer requirements format, you can still run `uv pip install -r requirements.txt`.

## Usage

From the repository root:

```bash
uv run streamlit run webapp/Main_Page.py
```

Then open the local Streamlit URL shown in your terminal.

## How It Works

1. Both input WAV files are loaded.
2. OpenUnmix separates vocals from each track.
3. Signals are trimmed, resampled, and segmented into frames.
4. Features are extracted and compared:
   - MFCCs for timbre/phonetic content.
   - Pitch and median-normalized pitch dynamics.
   - Short-term energy variation.
   - Singing power ratio over frequency bands.
5. A weighted error score is converted into a grade.

## Project Structure

- `webapp/Main_Page.py`: Landing page and app overview.
- `webapp/pages/evaluation_page.py`: Upload + evaluation UI.
- `webapp/eval_code.py`: Core audio processing and scoring logic.
- `model/`: OpenUnmix separator model files.

