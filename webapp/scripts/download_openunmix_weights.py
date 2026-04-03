from __future__ import annotations

import argparse
from pathlib import Path
import sys
from urllib.error import URLError
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webapp.app_paths import MODEL_DIR


WEIGHT_FILENAME = "vocals-b62c91ce.pth"
DEFAULT_URLS = (
    f"https://github.com/sigsep/open-unmix-pytorch/releases/download/v1.0.0/{WEIGHT_FILENAME}",
    f"https://zenodo.org/records/3370489/files/{WEIGHT_FILENAME}?download=1",
)


def download_file(target_path: Path, urls: tuple[str, ...]) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    for url in urls:
        try:
            print(f"Downloading {url} -> {target_path}")
            urlretrieve(url, target_path)
            print("Download complete.")
            return
        except URLError as exc:
            print(f"Download failed from {url}: {exc}")
    raise RuntimeError("Unable to download OpenUnmix weights from the configured URLs.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the OpenUnmix vocals weights used by the app.")
    parser.add_argument("--model-dir", type=Path, default=MODEL_DIR, help="Directory that contains OpenUnmix config files.")
    args = parser.parse_args()

    target_path = args.model_dir / WEIGHT_FILENAME
    if target_path.exists():
        print(f"Weights already exist at {target_path}")
        return

    download_file(target_path, DEFAULT_URLS)


if __name__ == "__main__":
    main()
