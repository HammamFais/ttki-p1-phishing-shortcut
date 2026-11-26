"""Mengambil angka baseline repo acuan ke results/baseline_reference.csv.

Sumber:
- "readme": tabel "Results (Full Metrics)" di readme.md repo acuan.
- "run ulang": output 02_Baseline.ipynb repo acuan yang dijalankan apa adanya (tanpa perubahan)
  di folder ../_reference/ dengan versi paket dari requirements.txt mereka.

Folder _reference/ tidak ikut repo ini. Jalankan dari folder repo:  python -m src.reference_results
"""
import json
import re

import pandas as pd

from src.data import REPO_ROOT

REF = REPO_ROOT.parent / "_reference"
README = REF / "PhiUSIIL-Phishing-URL-Detection" / "readme.md"
EXECUTED = REF / "02_Baseline_executed_2026-11-26.ipynb"
OUT = REPO_ROOT / "results" / "baseline_reference.csv"
METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc"]


def from_readme():
    text = README.read_text(encoding="utf-8")
    table = text.split("## **Results (Full Metrics)**")[1].split("\n\n")[1]
    rows = []
    for line in table.splitlines()[2:]:
        cells = [c.strip().strip("*") for c in line.strip("|").split("|")]
        rows.append({"source": "readme", "model": cells[0], **dict(zip(METRICS, map(float, cells[1:])))})
    return rows


def from_run():
    nb = json.loads(EXECUTED.read_text(encoding="utf-8"))
    text = "".join("".join(o["text"]) for c in nb["cells"] for o in c.get("outputs", []) if "text" in o)
    rows = []
    for block in text.split("=== ")[1:]:
        name, body = block.split(" ===", 1)
        vals = [float(v) for v in re.findall(r":\s*([0-9.]+)", body)]
        rows.append({"source": "run ulang 2026-11-26", "model": name, **dict(zip(METRICS, vals))})
    return rows


def main():
    out = pd.DataFrame(from_readme() + from_run())
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
