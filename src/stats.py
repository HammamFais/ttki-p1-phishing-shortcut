"""Uji statistik atas selisih F1 per seed. Hasil: results/stats.csv.

Efek dihitung per seed dalam poin persentase (pp): F3 - F2, F2 - F1, dan S2 - S1.
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
EFFECTS = [
    ("F3 - F2 pada S1", ("F3", "S1"), ("F2", "S1")),
    ("F3 - F2 pada S2", ("F3", "S2"), ("F2", "S2")),
    ("F2 - F1 pada S1", ("F2", "S1"), ("F1", "S1")),
    ("F2 - F1 pada S2", ("F2", "S2"), ("F1", "S2")),
    ("S2 - S1 pada F1", ("F1", "S2"), ("F1", "S1")),
    ("S2 - S1 pada F2", ("F2", "S2"), ("F2", "S1")),
    ("S2 - S1 pada F3", ("F3", "S2"), ("F3", "S1")),
]


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
    with pd.option_context("display.width", 200, "display.float_format", "{:.4f}".format):
        print(out.to_string(index=False))


if __name__ == "__main__":
    main()
