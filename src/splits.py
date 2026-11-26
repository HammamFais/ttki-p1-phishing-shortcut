"""Domain induk (eTLD+1) untuk pengelompokan split."""
import tldextract

# offline: pakai snapshot Public Suffix List bawaan tldextract, tanpa unduhan
# hanya bagian ICANN dari PSL (bawaan tldextract), jadi x.web.app -> web.app
_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())


def registered_domain(host):
    """eTLD+1 dari hostname. Host berupa IP atau tanpa suffix dikembalikan apa adanya."""
    host = str(host).strip().lower().rstrip(".")
    return _EXTRACT(host).top_domain_under_public_suffix or host
