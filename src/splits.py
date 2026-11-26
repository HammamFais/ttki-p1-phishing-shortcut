"""Domain induk (eTLD+1) dan dua strategi split.

S1: stratified random split 70/30.
S2: GroupShuffleSplit 70/30 dengan grup = domain induk (eTLD+1).
"""
import tldextract
from sklearn.model_selection import GroupShuffleSplit, train_test_split

TEST_SIZE = 0.3

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
    """Indeks baris train dan test untuk split 'S1' atau 'S2'."""
    idx = range(len(y))
    if split == "S1":
        tr, te = train_test_split(list(idx), test_size=TEST_SIZE, random_state=seed, stratify=y)
        return sorted(tr), sorted(te)
    if split == "S2":
        gss = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=seed)
        tr, te = next(gss.split(list(idx), y, groups))
        return list(tr), list(te)
    raise ValueError(split)
