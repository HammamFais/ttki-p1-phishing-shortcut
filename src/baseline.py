"""Reproduksi baseline. Hasil: results/baseline.csv.

Dua protokol dijalankan dengan kode yang ditulis sendiri:
- "acuan": meniru protokol repo pradhyumnaag30/PhiUSIIL-Phishing-URL-Detection (02_Baseline.ipynb):
  tanpa hapus duplikat, kelas positif = label 1 (legitimate), stratified 70/30 dengan seed 42,
  LR max_iter=10000 tanpa scaler, RF 200 pohon.
- "kita": protokol penelitian ini untuk sel F1 x S1: duplikat URL dihapus, phishing = positif,
  LR = StandardScaler + LogisticRegression(max_iter=1000), RF 100 pohon.

Jalankan dari folder repo:  python -m src.baseline
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.data import ID_COLUMNS, LABEL, REPO_ROOT, load_clean, load_raw

SEED = 42
OUT = REPO_ROOT / "results" / "baseline.csv"


def scores(model, X_tr, X_te, y_tr, y_te):
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    prob = model.predict_proba(X_te)[:, 1]
    return {"accuracy": accuracy_score(y_te, pred), "precision": precision_score(y_te, pred),
            "recall": recall_score(y_te, pred), "f1": f1_score(y_te, pred), "roc_auc": roc_auc_score(y_te, prob),
            "n_train": len(y_tr), "n_test": len(y_te)}


def run(protocol, df, y, models):
    X = df[[c for c in df.columns if c not in ID_COLUMNS + [LABEL, "y"]]]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=SEED, stratify=y)
    rows = []
    for name, model in models.items():
        rows.append({"protocol": protocol, "model": name, "n_features": X.shape[1], **scores(model, X_tr, X_te, y_tr, y_te)})
    return rows


def main():
    raw = load_raw()
    rows = run("acuan (label 1 = legitimate positif, tanpa dedup)", raw, raw[LABEL], {
        "LR": LogisticRegression(max_iter=10000),
        "RF": RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=-1),
    })
    clean = load_clean()
    rows += run("kita F1xS1 (phishing positif, dedup)", clean, clean["y"], {
        "LR": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "RF": RandomForestClassifier(n_estimators=100, random_state=SEED, n_jobs=-1),
    })
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
