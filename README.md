# Song Evaluation System

This Streamlit app evaluates a singer's cover against a reference track. It uses OpenUnmix for vocal separation, DTW for timing-aware alignment, SQLite for persistence, and a results dashboard to track progress over time.

## Developer Setup

### Option A: `python3 -m venv`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 webapp/scripts/download_openunmix_weights.py
streamlit run webapp/Main_Page.py
```

### Option B: `uv`

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
python3 webapp/scripts/download_openunmix_weights.py
streamlit run webapp/Main_Page.py
```

The app starts on port `8501` by default.

## Model Weights

The repo keeps the OpenUnmix JSON config files in `model/`, but the `vocals-b62c91ce.pth` weight file is intentionally not tracked.

Download the weight locally with:

```bash
python3 webapp/scripts/download_openunmix_weights.py
```

The script places the file in `model/` so the app can resolve it with relative paths.

## Calibration

The provisional calibration pipeline uses `scikit-learn` to fit metric weights from labeled cover examples.

```bash
python3 webapp/scripts/calibrate_scoring.py --manifest calibration/bootstrap_manifest.json
```

By default the script overwrites `webapp/config/scoring_weights.json`, which is what the app reads at runtime.

`calibration/bootstrap_manifest.json` is a bootstrap example that references the legacy local audio assets if they exist on disk. Replace it with your own labeled examples for more reliable fitted weights.

## Docker

Build and run the app in containers with:

```bash
docker compose up --build
```

## Project Layout

- `webapp/Main_Page.py`: landing page and app overview.
- `webapp/pages/1_Evaluation.py`: upload flow, cached model loading, evaluation, session state, and persistence.
- `webapp/pages/2_Results.py`: latest-result view and historical dashboard.
- `webapp/core/`: UI-free evaluation pipeline and scoring types.
- `webapp/services/`: database, storage, and model loading helpers.
- `webapp/scripts/`: weight download and scoring calibration scripts.
