"""Membaca CSV PhiUSIIL dan menyiapkan label serta kolom identitas."""
import os
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO_ROOT.parent / "PhiUSIIL_Phishing_URL_Dataset.csv"

# kolom teks/identitas yang tidak pernah dipakai sebagai fitur
ID_COLUMNS = ["FILENAME", "URL", "Domain", "TLD", "Title"]
LABEL = "label"


def csv_path():
    return Path(os.environ.get("PHIUSIIL_CSV", DEFAULT_CSV))


def load_raw():
    """CSV apa adanya. Label asli: 1 = legitimate, 0 = phishing."""
    return pd.read_csv(csv_path(), encoding_errors="replace")


def load_clean():
    """Hapus URL duplikat (baris pertama dipertahankan) dan balik label: phishing = 1."""
    df = load_raw()
    conflicts = df.groupby("URL")[LABEL].nunique()
    if (conflicts > 1).any():
        raise ValueError(f"{int((conflicts > 1).sum())} URL punya label bertentangan")
    df = df.drop_duplicates(subset="URL", keep="first").reset_index(drop=True)
    df["y"] = 1 - df[LABEL]
    return df
