"""Eksperimen utama: 4 set fitur (F1-F4) x 3 split (S1, S2, S2g) x 2 model x 5 seed = 120 run,
ditambah aturan R0. Desain brief awal (F1-F3 x S1/S2) adalah 60 run; F4 dan S2g ditambahkan kemudian
(lihat README, bagian Riwayat desain).

Hasil:
- results/metrics.csv       satu baris per run (termasuk R0)
- results/split_report.csv  komposisi train/test per split dan seed

Jalankan dari folder repo:  python -m src.run_experiments
"""
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.data import REPO_ROOT, load_clean
from src.features import F2_COLUMNS, F3_COLUMNS, TEMPLATE_FLAGS, build_f3, build_f4, f1_columns, r0_predict
from src.splits import registered_domain, split_indices

SEEDS = [7, 21, 42, 123, 2026]
SPLITS = ["S1", "S2", "S2g"]
RESULTS = REPO_ROOT / "results"


def make_model(name, seed):
    if name == "LR":
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    return RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=seed)


def evaluate(y_true, pred, score):
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred),
        "f1": f1_score(y_true, pred),
        "roc_auc": roc_auc_score(y_true, score),
        "pr_auc": average_precision_score(y_true, score),
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        "fnr": fn / (fn + tp), "fpr": fp / (fp + tn),
    }


def main():
    df = load_clean()
    y = df["y"].to_numpy()
    groups = df["Domain"].map(registered_domain).to_numpy()
    f3 = build_f3(df)
    feature_sets = {"F1": df[f1_columns(df)], "F2": df[F2_COLUMNS], "F3": f3, "F4": build_f4(df, f3)}
    assert list(feature_sets["F4"].columns) == F3_COLUMNS + TEMPLATE_FLAGS
    print({k: v.shape[1] for k, v in feature_sets.items()}, "fitur;", len(df), "baris")
    top10 = set(pd.Series(groups).value_counts().head(10).index)  # 10 domain induk terbesar

    rows, split_rows = [], []
    for seed in SEEDS:
        for split in SPLITS:
            tr, te = split_indices(split, y, groups, seed)
            g_tr, g_te = set(groups[tr]), set(groups[te])
            split_rows.append({
                "seed": seed, "split": split, "n_train": len(tr), "n_test": len(te),
                "test_frac": len(te) / len(y),
                "phishing_pct_train": 100 * y[tr].mean(), "phishing_pct_test": 100 * y[te].mean(),
                "reg_domains_train": len(g_tr), "reg_domains_test": len(g_te),
                "reg_domains_shared": len(g_tr & g_te),
                "top10_domain_rows_test": int(np.isin(groups[te], list(top10)).sum()),
                "top10_domains_in_test": int(len(top10 & g_te)),
            })
            base = {"seed": seed, "split": split, "n_train": len(tr), "n_test": len(te)}

            # R0: aturan templat, tanpa pelatihan
            t0 = time.perf_counter()
            pred = r0_predict(df["URL"].iloc[te]).to_numpy()
            t_inf = time.perf_counter() - t0
            rows.append({**base, "features": "R0", "model": "rule", "n_features": 0,
                         **evaluate(y[te], pred, pred), "train_time_s": 0.0,
                         "infer_ms_per_1000": 1000 * t_inf / len(te) * 1000})

            for fs, X in feature_sets.items():
                X_tr, X_te = X.iloc[tr], X.iloc[te]
                for name in ("LR", "RF"):
                    model = make_model(name, seed)
                    t0 = time.perf_counter()
                    model.fit(X_tr, y[tr])
                    t_fit = time.perf_counter() - t0
                    t0 = time.perf_counter()
                    score = model.predict_proba(X_te)[:, 1]
                    t_inf = time.perf_counter() - t0
                    pred = (score >= 0.5).astype(int)
                    rows.append({**base, "features": fs, "model": name, "n_features": X.shape[1],
                                 **evaluate(y[te], pred, score), "train_time_s": t_fit,
                                 "infer_ms_per_1000": 1000 * t_inf / len(te) * 1000})
                    r = rows[-1]
                    print(f"seed={seed} {split} {fs} {name}: F1={r['f1']:.5f} FN={r['fn']} FP={r['fp']} fit={t_fit:.1f}s")

    pd.DataFrame(rows).to_csv(RESULTS / "metrics.csv", index=False)
    pd.DataFrame(split_rows).to_csv(RESULTS / "split_report.csv", index=False)
    print("selesai:", len(rows), "baris metrics")


if __name__ == "__main__":
    main()
