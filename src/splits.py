"""Domain induk (eTLD+1) dan strategi split.

S1:  stratified random split 70/30.
S2:  StratifiedGroupKFold(n_splits=10, shuffle=True) dengan grup = domain induk (eTLD+1);
     3 dari 10 fold, dipilih acak per seed, digabung menjadi data uji (30%); 7 fold sisanya data latih.
S2g: GroupShuffleSplit 70/30 dengan grup = domain induk. Desain awal S2; dipertahankan sebagai
     analisis sensitivitas karena proporsi phishing di data ujinya tidak dijaga.
"""
import numpy as np
import tldextract
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold, train_test_split

TEST_SIZE = 0.3
SGKF_FOLDS, SGKF_TEST_FOLDS = 10, 3

# offline: pakai snapshot Public Suffix List bawaan tldextract, tanpa unduhan
# hanya bagian ICANN dari PSL (bawaan tldextract), jadi x.web.app -> web.app
_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())


def bare_host(host):
    """Hostname huruf kecil tanpa port dan titik di akhir."""
    host = str(host).strip().lower().rstrip(".")
    if host.startswith("["):  # IPv6 literal
        return host.split("]")[0] + "]"
    return host.rsplit(":", 1)[0] if host.count(":") == 1 else host


def registered_domain(host):
    """eTLD+1 dari hostname. Host berupa IP atau tanpa suffix dikembalikan apa adanya."""
    host = bare_host(host)
    return _EXTRACT(host).top_domain_under_public_suffix or host


def split_indices(split, y, groups, seed):
    """Indeks baris train dan test untuk split 'S1', 'S2', atau 'S2g'."""
    idx = np.arange(len(y))
    if split == "S1":
        tr, te = train_test_split(idx, test_size=TEST_SIZE, random_state=seed, stratify=y)
        return np.sort(tr), np.sort(te)
    if split == "S2":
        sgkf = StratifiedGroupKFold(n_splits=SGKF_FOLDS, shuffle=True, random_state=seed)
        folds = [te for _, te in sgkf.split(idx, y, groups)]
        # grup terbesar selalu ditempatkan di fold-fold awal, jadi fold uji dipilih acak per seed
        pick = np.random.default_rng(seed).choice(SGKF_FOLDS, SGKF_TEST_FOLDS, replace=False)
        te = np.sort(np.concatenate([folds[i] for i in pick]))
        return np.setdiff1d(idx, te), te
    if split == "S2g":
        gss = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=seed)
        tr, te = next(gss.split(idx, y, groups))
        return tr, te  # urutan sama dengan run tahap 4 agar hasilnya identik
    raise ValueError(split)
