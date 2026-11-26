"""Uji statistik atas selisih F1 per seed. Hasil: results/stats.csv.

Efek dihitung per seed dalam poin persentase (pp): selisih antar set fitur di setiap split,
dan selisih S2 - S1 serta S2g - S1 untuk setiap set fitur.
Metrik utama F1; ROC-AUC (x100) diuji juga sebagai pembanding karena pada S2 proporsi
phishing di data uji berubah antar seed, dan F1 ikut terpengaruh proporsi itu.
Paired t-test dua sisi dengan IK 95%; Wilcoxon signed-rank sebagai pembanding
(untuk n = 5, p dua sisi terkecil yang mungkin adalah 0,0625).

Jalankan dari folder repo:  python -m src.stats
"""
import numpy as np
import pandas as pd
from scipy import stats

from src.data import REPO_ROOT

RESULTS = REPO_ROOT / "results"

# (nama efek, kondisi pembanding, kondisi acuan); selisih = pembanding - acuan
# F4 - F3 dan F4 - F2: tambahan untuk memisahkan efek templat dari efek jumlah fitur.
# S2g: analisis sensitivitas (GroupShuffleSplit, desain awal S2).
FEATURE_PAIRS = [("F3", "F2"), ("F2", "F1"), ("F4", "F3"), ("F4", "F2")]
EFFECTS = (
    [(f"{a} - {b} pada {s}", (a, s), (b, s)) for s in ("S1", "S2", "S2g") for a, b in FEATURE_PAIRS]
    + [(f"{s} - S1 pada {f}", (f, s), (f, "S1")) for s in ("S2", "S2g") for f in ("F1", "F2", "F3", "F4")]
)


def per_seed(m, model, features, split, metric):
    s = m[(m.model == model) & (m.features == features) & (m.split == split)].set_index("seed")[metric]
    return 100 * s.sort_index()


def test(diff):
    n = len(diff)
    mean, sd = diff.mean(), diff.std(ddof=1)
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    t = stats.ttest_rel(diff, np.zeros(n)) if sd > 0 else None
    w = stats.wilcoxon(diff) if (diff != 0).any() else None
    return {
        "n_seeds": n, "mean_diff_pp": mean, "sd_pp": sd, "ci95_low_pp": mean - half, "ci95_high_pp": mean + half,
        "t": t.statistic if t else np.nan, "p_ttest": t.pvalue if t else np.nan,
        "wilcoxon_W": w.statistic if w else np.nan, "p_wilcoxon": w.pvalue if w else np.nan,
        "n_negative": int((diff < 0).sum()), "n_positive": int((diff > 0).sum()),
    }


def main():
    m = pd.read_csv(RESULTS / "metrics.csv")
    rows = []
    # f1 = metrik utama; roc_auc = pembanding yang tidak bergantung pada proporsi kelas di test
    for metric in ("f1", "roc_auc"):
        for model in ("LR", "RF"):
            for name, (fa, sa), (fb, sb) in EFFECTS:
                a, b = per_seed(m, model, fa, sa, metric), per_seed(m, model, fb, sb, metric)
                assert list(a.index) == list(b.index)
                rows.append({"effect": name, "model": model, "metric": metric, **test((a - b).to_numpy())})
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "stats.csv", index=False)

    # hubungan komposisi data uji dengan F1 pada split berbasis grup (Pearson, n = 5 seed)
    s = pd.read_csv(RESULTS / "split_report.csv")
    corr = []
    for split in ("S2", "S2g"):
        comp = s[s.split == split][["seed", "phishing_pct_test", "top10_domain_rows_test"]]
        for model in ("LR", "RF"):
            d = m[(m.split == split) & (m.features == "F3") & (m.model == model)].merge(comp, on="seed")
            for col in ("phishing_pct_test", "top10_domain_rows_test"):
                r, p = stats.pearsonr(d[col], d["f1"]) if d[col].nunique() > 1 else (np.nan, np.nan)
                corr.append({"split": split, "features": "F3", "model": model, "x": col, "y": "f1",
                             "pearson_r": r, "p": p, "n_seeds": len(d)})
    pd.DataFrame(corr).to_csv(RESULTS / "composition_corr.csv", index=False)
    with pd.option_context("display.width", 200, "display.float_format", "{:.4f}".format):
        print(out.to_string(index=False))


if __name__ == "__main__":
    main()
