"""Audit dataset PhiUSIIL. Hasil: results/audit.json.

Jalankan dari folder repo:  python -m src.audit
"""
import hashlib
import json
import platform
from urllib.parse import urlsplit

import numpy as np
import pandas as pd
import sklearn
import tldextract
from sklearn.metrics import roc_auc_score

from src.data import ID_COLUMNS, LABEL, REPO_ROOT, csv_path, load_raw
from src.features import TEMPLATE_RE
from src.splits import registered_domain

OUT = REPO_ROOT / "results" / "audit.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def template_parts(url):
    p = urlsplit(url)
    host = p.netloc.lower()
    return {
        "https": p.scheme.lower() == "https",
        "www": host.startswith("www."),
        "no_path_query": p.path in ("", "/") and not p.query and not p.fragment,
        "r0_match": bool(TEMPLATE_RE.match(url)),
    }


def share(mask):
    return {"n": int(mask.sum()), "pct": round(100 * float(mask.mean()), 2)}


def main():
    path = csv_path()
    df = load_raw()
    y = 1 - df[LABEL]  # phishing = 1
    numeric = [c for c in df.columns if c not in ID_COLUMNS + [LABEL]]
    non_numeric = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    assert sorted(non_numeric) == sorted(ID_COLUMNS), non_numeric

    out = {"file": {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}}

    # --- ukuran, nilai kosong, duplikat ---
    url_counts = df["URL"].value_counts()
    dup_urls = url_counts[url_counts > 1]
    conflict = df[df["URL"].isin(dup_urls.index)].groupby("URL")[LABEL].nunique()
    out["shape"] = {
        "rows": len(df), "columns": df.shape[1],
        "missing_values": int(df.isna().sum().sum()),
        "infinite_values": int(np.isinf(df[numeric].to_numpy(dtype=float)).sum()),
        "full_row_duplicates": int(df.duplicated().sum()),
    }
    out["label_original"] = {"legitimate_1": int((df[LABEL] == 1).sum()), "phishing_0": int((df[LABEL] == 0).sum())}
    out["url_duplicates"] = {
        "urls_appearing_more_than_once": int(len(dup_urls)),
        "extra_rows_removed": int((dup_urls - 1).sum()),
        "urls_with_label_conflict": int((conflict > 1).sum()),
        "duplicate_rows_by_label": {k: int(v) for k, v in
                                    df[df.duplicated("URL", keep="first")][LABEL].map({1: "legitimate", 0: "phishing"}).value_counts().items()},
    }
    dedup = df.drop_duplicates("URL", keep="first")
    out["after_dedup"] = {"rows": len(dedup), "legitimate": int((dedup[LABEL] == 1).sum()), "phishing": int((dedup[LABEL] == 0).sum())}
    out["columns"] = {"non_numeric": non_numeric, "id_text_excluded": ID_COLUMNS, "numeric_feature_count": len(numeric)}

    # --- FILENAME bocor ---
    mw = df["FILENAME"].astype(str).str.startswith("mw")
    out["filename_mw_prefix"] = {"rows": int(mw.sum()), "phishing_among_them": int(y[mw].sum())}

    # --- templat URL sah per label ---
    parts = pd.DataFrame([template_parts(u) for u in df["URL"]])
    parts["sim100"] = (df["URLSimilarityIndex"] == 100).to_numpy()
    tmpl = {}
    for name, lab in (("legitimate", 0), ("phishing", 1)):
        sub = parts[(y == lab).to_numpy()]
        tmpl[name] = {"rows": len(sub), **{c: share(sub[c]) for c in parts.columns}}
    out["template_by_label"] = tmpl

    # --- ROC-AUC satu fitur (phishing = positif); 'oriented' = max(AUC, 1-AUC) ---
    aucs = []
    for c in numeric:
        a = roc_auc_score(y, df[c])
        aucs.append({"feature": c, "auc": round(a, 4), "oriented_auc": round(max(a, 1 - a), 4)})
    aucs.sort(key=lambda r: -r["oriented_auc"])
    out["single_feature_auc_top10"] = aucs[:10]

    # --- hostname dan domain induk (eTLD+1) ---
    host = df["Domain"].astype(str).str.lower()
    reg = host.map(registered_domain)
    reg_counts = reg.value_counts()
    multi = reg_counts[reg_counts > 1]
    reg_label = pd.DataFrame({"reg": reg, "y": y}).groupby("reg")["y"].agg(["size", "mean"])
    out["hostname"] = {"unique": int(host.nunique()), "rows": len(df)}
    out["registered_domain"] = {
        "method": "tldextract top_domain_under_public_suffix, ICANN PSL snapshot bawaan (offline)",
        "unique": int(reg.nunique()),
        "appearing_more_than_once": int(len(multi)),
        "rows_in_those": int(multi.sum()),
        "mixed_label_domains": int(((reg_label["mean"] > 0) & (reg_label["mean"] < 1)).sum()),
        "top10": [{"domain": d, "rows": int(n), "phishing_pct": round(100 * float(reg_label.loc[d, "mean"]), 1)}
                  for d, n in reg_counts.head(10).items()],
    }
    out["environment"] = {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__,
                          "scikit_learn": sklearn.__version__, "tldextract": tldextract.__version__,
                          "os": platform.platform()}

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
