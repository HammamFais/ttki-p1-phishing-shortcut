"""Gambar dan tabel untuk paper, dibuat langsung dari results/.

Hasil:
- figures/fig1_alur_eksperimen.png
- figures/fig2_f1_fn_per_skenario.png
- figures/fig3_komposisi_uji_s2g.png
- figures/tables.md   (tabel Markdown, desimal memakai koma)

Jalankan dari folder repo:  python -m src.make_figures
"""
import json
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter, NullFormatter

from src.data import REPO_ROOT

RESULTS = REPO_ROOT / "results"
FIG = REPO_ROOT / "figures"

# palet kategori (diuji CVD); identitas juga dibawa bentuk penanda
COLOR = {"LR": "#2a78d6", "RF": "#eb6834", "rule": "#1baf7a"}
MARKER = {"LR": "o", "RF": "s", "rule": "D"}
LABEL = {"LR": "Logistic Regression", "RF": "Random Forest", "rule": "R0 (aturan templat)"}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
FEATURES = ["R0", "F1", "F2", "F3", "F4"]
# nama tampilan di paper agar tidak bentrok dengan metrik F1; kode dan CSV tetap memakai F1-F4
DISPLAY = {"R0": "R0", "F1": "FL", "F2": "FU", "F3": "FH", "F4": "FHT"}


def disp(text):
    """Ganti kode set fitur F1-F4 dengan nama tampilan (dipakai untuk nilai, bukan nama metrik)."""
    return re.sub(r"\bF([1-4])\b", lambda mm: DISPLAY[mm.group(0)], str(text))

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Segoe UI", "Verdana"], "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.dpi": 300,
})


def num(x, d=2):
    """Angka dengan koma desimal, titik ribuan, dan tanda minus tipografis."""
    if round(x, d) == 0:
        x = 0.0  # hindari "-0,00"
    s = f"{x:,.{d}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".").replace("-", "−")


def pm(mean, sd, d=2):
    return f"{num(mean, d)} ± {num(sd, d)}"


# ---------------------------------------------------------------- gambar 1
def fig_flow(audit):
    steps = [
        f"CSV PhiUSIIL (Kaggle)\n{num(audit['shape']['rows'], 0)} URL, 56 kolom",
        f"Audit dan hapus {audit['url_duplicates']['extra_rows_removed']} URL duplikat\n"
        f"{num(audit['after_dedup']['rows'], 0)} URL; phishing = kelas positif",
        "Set fitur\nR0 (aturan), FL (50), FU (22), FH (10), FHT (13)",
        "Split 70/30 per seed (7, 21, 42, 123, 2026)\nS1 acak berstrata | S2 grup eTLD+1 berstrata | S2g grup eTLD+1",
        "Latih LR (scaler di pipeline) dan RF\nhanya pada data latih, hiperparameter bawaan",
        "Evaluasi di data uji\nF1, recall, ROC-AUC, PR-AUC, FN, FP, waktu",
        "Uji statistik per seed\npaired t-test + IK 95%, Wilcoxon",
    ]
    fig, ax = plt.subplots(figsize=(6.2, 6.6))
    ax.set_axis_off()
    h, gap = 0.105, 0.035
    for i, text in enumerate(steps):
        y = 1 - i * (h + gap) - h
        ax.add_patch(FancyBboxPatch((0.08, y), 0.84, h, boxstyle="round,pad=0.008,rounding_size=0.02",
                                    linewidth=1, edgecolor=MUTED, facecolor="#f4f3f0"))
        ax.text(0.5, y + h / 2, text, ha="center", va="center", fontsize=8.5, color=INK, linespacing=1.4)
        if i < len(steps) - 1:
            ax.annotate("", xy=(0.5, y - gap + 0.004), xytext=(0.5, y - 0.004),
                        arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1))
    ax.set_xlim(0, 1)
    ax.set_ylim(1 - len(steps) * (h + gap), 1.01)
    fig.savefig(FIG / "fig1_alur_eksperimen.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- gambar 2
def fig_f1_fn(m):
    splits = ["S1", "S2"]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2), sharex=True)
    x = np.arange(len(FEATURES))
    offset = {"LR": -0.12, "RF": 0.12, "rule": 0.0}
    for col, split in enumerate(splits):
        sub = m[m.split == split]
        for row, (metric, ylabel) in enumerate([("f1", "F1-score"), ("fn", "Jumlah FN (skala log)")]):
            ax = axes[row, col]
            for model in ("rule", "LR", "RF"):
                d = sub[sub.model == model].groupby("features")[metric].agg(["mean", "std"])
                d = d.reindex(FEATURES).dropna()
                xs = [x[FEATURES.index(f)] + offset[model] for f in d.index]
                vals = d["mean"].clip(lower=0.5) if metric == "fn" else d["mean"]
                ax.errorbar(xs, vals, yerr=d["std"], fmt=MARKER[model], color=COLOR[model], ms=6,
                            mec=SURFACE, mew=1, elinewidth=1, capsize=0, label=LABEL[model])
            ax.grid(axis="y", color=GRID, lw=0.6)
            ax.set_axisbelow(True)
            if metric == "fn":
                ax.set_yscale("log")
                ax.set_ylim(0.3, 3e4)
                ax.set_yticks([1, 10, 100, 1000, 10000])
                ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: num(v, 0)))
                ax.yaxis.set_minor_formatter(NullFormatter())
            else:
                ax.set_ylim(0.6, 1.02)
                ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: num(v, 1)))
            if col == 0:
                ax.set_ylabel(ylabel)
            if row == 0:
                ax.set_title(f"{split}: " + ("stratified random split" if split == "S1" else "grup eTLD+1 berstrata"),
                             fontsize=9, color=INK, loc="left")
    for ax in axes[1]:
        ax.set_xticks(x, [DISPLAY[f] for f in FEATURES])
        ax.set_xlabel("Set fitur")
    handles = [Line2D([], [], ls="", marker=MARKER[k], color=COLOR[k], ms=6, mec=SURFACE) for k in ("rule", "LR", "RF")]
    fig.legend(handles, [LABEL[k] for k in ("rule", "LR", "RF")], loc="lower center", ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(FIG / "fig2_f1_fn_per_skenario.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- gambar 3
def fig_composition(m, s):
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    for split, filled in (("S2g", True), ("S2", False)):
        comp = s[s.split == split][["seed", "phishing_pct_test"]]
        d = m[(m.split == split) & (m.features == "F3")].merge(comp, on="seed")
        for model in ("LR", "RF"):
            dd = d[d.model == model]
            ax.scatter(dd.phishing_pct_test, dd.f1, marker=MARKER[model], s=42,
                       facecolor=COLOR[model] if filled else SURFACE, edgecolor=COLOR[model], linewidth=1.3,
                       label=f"{LABEL[model]}, {split}")
    ax.set_xlabel("Proporsi phishing di data uji (%)")
    ax.set_ylabel("F1-score pada FH")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: num(v, 3)))
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_komposisi_uji_s2g.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- tabel
def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    return "\n".join(out)


def tables(audit, m, s, st):
    parts = []
    a = audit
    rd = a["registered_domain"]
    parts.append("## Tabel 1. Karakteristik dataset\n\n" + md_table(["Butir", "Nilai"], [
        ["Baris pada CSV asli", num(a["shape"]["rows"], 0)],
        ["Kolom", a["shape"]["columns"]],
        ["Nilai kosong / tak hingga / baris duplikat penuh", f"{a['shape']['missing_values']} / {a['shape']['infinite_values']} / {a['shape']['full_row_duplicates']}"],
        ["Label asli: sah (1) / phishing (0)", f"{num(a['label_original']['legitimate_1'], 0)} / {num(a['label_original']['phishing_0'], 0)}"],
        ["URL duplikat yang dihapus (semuanya phishing, tanpa konflik label)", a["url_duplicates"]["extra_rows_removed"]],
        ["Baris setelah dedup: sah / phishing", f"{num(a['after_dedup']['legitimate'], 0)} / {num(a['after_dedup']['phishing'], 0)}"],
        ["Fitur numerik bawaan", a["columns"]["numeric_feature_count"]],
        ["Baris dengan FILENAME berawalan 'mw' (semuanya phishing)", num(a["filename_mw_prefix"]["rows"], 0)],
        ["Hostname unik", num(a["hostname"]["unique"], 0)],
        ["Domain induk (eTLD+1) unik", num(rd["unique"], 0)],
        ["Domain induk yang muncul lebih dari sekali / baris di dalamnya", f"{num(rd['appearing_more_than_once'], 0)} / {num(rd['rows_in_those'], 0)}"],
        ["Domain induk dengan label campuran", rd["mixed_label_domains"]],
    ]))

    t = a["template_by_label"]
    def cell(lab, k):
        return f"{num(t[lab][k]['n'], 0)} ({num(t[lab][k]['pct'], 2)}%)"
    parts.append("## Tabel 2. Ciri templat URL per label (CSV asli)\n\n" + md_table(
        ["Ciri", "Sah (n = " + num(t["legitimate"]["rows"], 0) + ")", "Phishing (n = " + num(t["phishing"]["rows"], 0) + ")"], [
            ["Skema https", cell("legitimate", "https"), cell("phishing", "https")],
            ["Host diawali www.", cell("legitimate", "www"), cell("phishing", "www")],
            ["Tanpa path, query, fragmen", cell("legitimate", "no_path_query"), cell("phishing", "no_path_query")],
            ["URLSimilarityIndex = 100", cell("legitimate", "sim100"), cell("phishing", "sim100")],
            ["Cocok persis dengan aturan R0", cell("legitimate", "r0_match"), cell("phishing", "r0_match")],
        ]))

    def result_table(split, title):
        rows = []
        sub = m[m.split == split]
        for f in FEATURES:
            for model in (("rule",) if f == "R0" else ("LR", "RF")):
                d = sub[(sub.features == f) & (sub.model == model)]
                if d.empty:
                    continue
                g = lambda c, k=100: (d[c].mean() * k, d[c].std() * k)
                rows.append([disp(f), "aturan" if model == "rule" else model, d.n_features.iloc[0],
                             pm(*g("f1")), pm(*g("recall")), pm(*g("precision")), pm(*g("roc_auc")), pm(*g("pr_auc")),
                             pm(*g("fn", 1), 1), pm(*g("fp", 1), 1)])
        return f"## {title}\n\n" + md_table(
            ["Fitur", "Model", "Jml. fitur", "F1 (%)", "Recall (%)", "Precision (%)", "ROC-AUC (×100)", "PR-AUC (×100)", "FN", "FP"], rows)

    parts.append(result_table("S1", "Tabel 3a. Hasil pada S1, rata-rata ± simpangan baku 5 seed"))
    parts.append(result_table("S2", "Tabel 3b. Hasil pada S2, rata-rata ± simpangan baku 5 seed"))
    parts.append(result_table("S2g", "Tabel 3c. Analisis sensitivitas S2g (GroupShuffleSplit), rata-rata ± simpangan baku 5 seed"))

    rows = []
    f1s = st[st.metric == "f1"]
    for _, r in f1s.iterrows():
        p = r.p_ttest
        rows.append([disp(r.effect).replace(" - ", " − "), r.model, num(r.mean_diff_pp, 2), f"[{num(r.ci95_low_pp, 2)}; {num(r.ci95_high_pp, 2)}]",
                     "–" if np.isnan(p) else ("< 0,0001" if p < 1e-4 else num(p, 4)),
                     "–" if np.isnan(r.p_wilcoxon) else num(r.p_wilcoxon, 4), f"{r.n_negative}/{r.n_positive}"])
    parts.append("## Tabel 4. Selisih F1 per seed (poin persentase)\n\n"
                 "Kolom terakhir: jumlah seed dengan selisih negatif/positif. Untuk n = 5, p Wilcoxon dua sisi terkecil adalah 0,0625.\n\n"
                 + md_table(["Efek", "Model", "Rata-rata (pp)", "IK 95% (pp)", "p (paired t)", "p (Wilcoxon)", "Neg/Pos"], rows))

    rows = []
    for split in ("S2", "S2g"):
        for _, r in s[s.split == split].iterrows():
            f3 = m[(m.split == split) & (m.features == "F3") & (m.seed == r.seed)].set_index("model").f1
            rows.append([split, r.seed, num(r.n_test, 0), num(100 * r.test_frac, 1), num(r.phishing_pct_test, 2),
                         r.reg_domains_shared, f"{r.top10_domains_in_test} ({num(r.top10_domain_rows_test, 0)})",
                         num(100 * f3["LR"], 2), num(100 * f3["RF"], 2)])
    parts.append("## Tabel 5. Komposisi data uji per seed pada split berbasis grup\n\n"
                 + md_table(["Split", "Seed", "n uji", "Porsi uji (%)", "Phishing di uji (%)", "Domain induk di train dan uji",
                             "Domain top-10 di uji (baris)", "F1 FH LR (%)", "F1 FH RF (%)"], rows))

    (FIG / "tables.md").write_text("# Tabel untuk paper\n\nDibuat otomatis oleh `python -m src.make_figures` dari `results/`. Jangan disunting manual.\n\n"
                                  "Nama set fitur: FL = F1, FU = F2, FH = F3, FHT = F4 pada kode dan CSV.\n\n"
                                  + "\n\n".join(parts) + "\n", encoding="utf-8")


def main():
    FIG.mkdir(exist_ok=True)
    audit = json.loads((RESULTS / "audit.json").read_text(encoding="utf-8"))
    m = pd.read_csv(RESULTS / "metrics.csv")
    s = pd.read_csv(RESULTS / "split_report.csv")
    st = pd.read_csv(RESULTS / "stats.csv")
    fig_flow(audit)
    fig_f1_fn(m)
    fig_composition(m, s)
    tables(audit, m, s, st)
    print("selesai:", sorted(p.name for p in FIG.iterdir()))


if __name__ == "__main__":
    main()
