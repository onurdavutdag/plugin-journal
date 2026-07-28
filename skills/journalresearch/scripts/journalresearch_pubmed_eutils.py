#!/usr/bin/env python3
"""Search PubMed via NCBI E-utilities — no authentication required.

Part of the `journalresearch` skill. Fallback for when the claude.ai PubMed/Consensus MCP
connectors are not authorized (e.g. non-interactive sessions). The public NCBI
E-utilities REST API needs no OAuth and no API key for light use, so this keeps the
skill's Step 2 (external evidence) working when the MCP tools are unavailable.

Usage:
    python journalresearch_pubmed_eutils.py --query "dexmedetomidine postoperative delirium" --retmax 5
    python journalresearch_pubmed_eutils.py --pmid 34567890            # fetch one record's metadata
    python journalresearch_pubmed_eutils.py --doi 10.1001/jama.2019.4783  # resolve a DOI to a PMID/record

Output: JSON to stdout — a list of records:
    [{"pmid","title","authors","journal","year","volume","issue","pages","doi","url"}]

Every record returned is a real, retrieved PubMed record — never reconstructed. Verify
the DOI/PMID against the paper before citing (same rule as the MCP path).

NCBI etiquette: <=3 requests/second without an API key, 10/s with one. This script
sleeps between calls, sets a descriptive User-Agent and identifies the caller with a
real address. Both are configurable through the environment:
    NCBI_EMAIL    contact address sent as the `email` parameter
    NCBI_API_KEY  personal API key (https://account.ncbi.nlm.nih.gov/settings/)
If NCBI is unreachable it returns a JSON
{"error": ...} and exit code 0 so the caller can parse the failure and fall back to
telling the user to authorize the MCP connector.
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
_UA = "research-skill/1.0 (Claude Code; academic citation assistant)"
_TOOL = "claude-research-skill"
# NCBI wants a REAL contact address so it can reach the caller before blocking it —
# but it must be THIS user's address. A hardcoded fallback made every third-party
# install sign its queries with the plugin author, who would then be the one NCBI
# contacts about someone else's traffic. Unset = the `email` parameter is simply
# omitted (E-utilities still answers) and a one-line warning goes to stderr.
# An API key in NCBI_API_KEY raises the rate limit 3 -> 10/s.
_EMAIL = os.environ.get("NCBI_EMAIL", "").strip()
_API_KEY = os.environ.get("NCBI_API_KEY") or ""
# Polite gap between two calls: ~3/s without a key, ~10/s with one.
_GAP = 0.11 if _API_KEY else 0.4


def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    return urllib.request.urlopen(req, timeout=timeout).read()


def _common_params(extra):
    p = {"tool": _TOOL}
    if _EMAIL:
        p["email"] = _EMAIL
    if _API_KEY:
        p["api_key"] = _API_KEY
    p.update(extra)
    return urllib.parse.urlencode(p)


def esearch(term, retmax):
    """Return a list of PMIDs matching term (relevance-sorted)."""
    q = _common_params({
        "db": "pubmed", "term": term, "retmax": str(retmax),
        "retmode": "json", "sort": "relevance",
    })
    data = json.loads(_get(f"{_BASE}/esearch.fcgi?{q}"))
    return data.get("esearchresult", {}).get("idlist", [])


def _text(node, path, default=""):
    el = node.find(path)
    return el.text if (el is not None and el.text) else default


def efetch(pmids):
    """Fetch full metadata for a list of PMIDs via efetch XML."""
    if not pmids:
        return []
    q = _common_params({
        "db": "pubmed", "id": ",".join(pmids), "retmode": "xml",
    })
    xml = _get(f"{_BASE}/efetch.fcgi?{q}")
    root = ET.fromstring(xml)
    records = []
    for art in root.findall(".//PubmedArticle"):
        medline = art.find(".//MedlineCitation")
        article = medline.find("Article") if medline is not None else None
        if article is None:
            continue
        pmid = _text(medline, "PMID")
        title = "".join(article.find("ArticleTitle").itertext()).strip() \
            if article.find("ArticleTitle") is not None else ""

        authors = []
        for a in article.findall(".//Author"):
            last = _text(a, "LastName")
            initials = _text(a, "Initials")
            collective = _text(a, "CollectiveName")
            if last:
                authors.append(f"{last} {initials}".strip())
            elif collective:
                authors.append(collective)

        journal = _text(article, ".//Journal/Title") or \
            _text(article, ".//Journal/ISOAbbreviation")
        year = _text(article, ".//JournalIssue/PubDate/Year") or \
            _text(article, ".//JournalIssue/PubDate/MedlineDate")[:4]
        volume = _text(article, ".//JournalIssue/Volume")
        issue = _text(article, ".//JournalIssue/Issue")
        pages = _text(article, ".//Pagination/MedlinePgn")

        doi = ""
        for eid in art.findall(".//ArticleIdList/ArticleId"):
            if eid.get("IdType") == "doi" and eid.text:
                doi = eid.text.strip()
                break
        if not doi:
            for eid in article.findall(".//ELocationID"):
                if eid.get("EIdType") == "doi" and eid.text:
                    doi = eid.text.strip()
                    break

        records.append({
            "pmid": pmid,
            "title": title,
            "authors": authors,
            "journal": journal,
            "year": year,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "doi": doi,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
        })
    return records


def by_doi(doi, retmax=5):
    pmids = esearch(f"{doi}[AID] OR {doi}[DOI]", retmax)
    time.sleep(_GAP)      # NCBI etiquette between esearch and efetch (as in main())
    return efetch(pmids)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Search/verify PubMed via E-utilities (no auth).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--query", help="Free-text PubMed query.")
    g.add_argument("--pmid", nargs="+", help="One or more PMIDs to fetch metadata for.")
    g.add_argument("--doi", help="Resolve a DOI to its PubMed record.")
    ap.add_argument("--retmax", type=int, default=5, help="Max results for --query/--doi (default 5).")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if not _EMAIL:
        sys.stderr.write(
            "UYARI: NCBI_EMAIL ayarlı değil — istekler iletişim adresi olmadan gönderiliyor. "
            "NCBI yoğun kullanımda adresi olmayan çağrıları engelleyebilir; "
            "kendi adresinizi NCBI_EMAIL ortam değişkenine yazın.\n")

    try:
        if args.pmid:
            result = efetch(args.pmid)
        elif args.doi:
            result = by_doi(args.doi, args.retmax)
        else:
            pmids = esearch(args.query, args.retmax)
            time.sleep(_GAP)  # NCBI etiquette between esearch and efetch
            result = efetch(pmids)
    except Exception as e:
        print(json.dumps({
            "error": "eutils_unreachable",
            "message": (
                f"NCBI E-utilities request failed: {e}. If this persists, the PubMed/"
                "Consensus MCP connector must be authorized in claude.ai connector settings."
            ),
        }))
        return 0

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
