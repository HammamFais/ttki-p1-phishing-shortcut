"""Definisi set fitur F1, F2, F3 dan aturan R0."""
import math
import re
from collections import Counter
from ipaddress import ip_address

import pandas as pd
import tldextract

from src.data import ID_COLUMNS, LABEL
from src.splits import bare_host

# R0: URL dianggap sah bila persis mengikuti templat https://www.<host>/ (tanpa path, query, fragmen)
TEMPLATE_RE = re.compile(r"^https://www\.[^/?#]+/?$")

# F2: fitur URL bawaan dataset (dihitung dari string URL, tanpa mengunduh halaman)
F2_COLUMNS = [
    "URLLength", "DomainLength", "IsDomainIP", "TLDLength", "NoOfSubDomain", "HasObfuscation",
    "NoOfObfuscatedChar", "ObfuscationRatio", "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL",
    "DegitRatioInURL", "NoOfEqualsInURL", "NoOfQMarkInURL", "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL", "SpacialCharRatioInURL", "IsHTTPS", "CharContinuationRate",
    "TLDLegitimateProb", "URLCharProb", "URLSimilarityIndex",
]

F3_COLUMNS = [
    "host_length", "host_labels", "host_digits", "host_digit_ratio", "host_hyphens", "host_letters",
    "host_longest_label", "host_tld_length", "host_is_ip", "host_entropy",
]

_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())


def f1_columns(df):
    """F1: semua fitur numerik bawaan (URL + isi halaman), tanpa kolom identitas dan label."""
    return [c for c in df.columns if c not in ID_COLUMNS + [LABEL, "y"]]


def _is_ip(host):
    try:
        ip_address(host.strip("[]"))
        return 1
    except ValueError:
        return 0


def _entropy(s):
    n = len(s)
    return -sum(k / n * math.log2(k / n) for k in Counter(s).values()) if n else 0.0


def host_features(domain):
    """F3: fitur host yang dihitung ulang dari hostname setelah awalan 'www.' dibuang.

    Skema, 'www', path, dan query tidak ikut, sehingga templat URL sah tidak bisa dipakai model.
    """
    host = bare_host(domain)
    if host.startswith("www."):
        host = host[4:]
    labels = host.split(".")
    digits = sum(ch.isdigit() for ch in host)
    is_ip = _is_ip(host)
    return {
        "host_length": len(host),
        "host_labels": len(labels),
        "host_digits": digits,
        "host_digit_ratio": digits / len(host) if host else 0.0,
        "host_hyphens": host.count("-"),
        "host_letters": sum(ch.isalpha() for ch in host),
        "host_longest_label": max(map(len, labels)),
        "host_tld_length": 0 if is_ip else len(_EXTRACT(host).suffix),
        "host_is_ip": is_ip,
        "host_entropy": _entropy(host),
    }


def build_f3(df):
    return pd.DataFrame([host_features(d) for d in df["Domain"]], index=df.index)[F3_COLUMNS]


def r0_predict(urls):
    """1 = phishing bila URL tidak cocok templat sah, 0 = sah."""
    return urls.map(lambda u: 0 if TEMPLATE_RE.match(u) else 1).astype(int)
