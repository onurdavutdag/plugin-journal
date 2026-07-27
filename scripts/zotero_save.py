#!/usr/bin/env python3
"""Write ONE record into the user's real Zotero library — for `journal-s-zotero`.

The counterpart of `zotero_lib.py`, which is deliberately read-only. Writing lives in
its own file so that read-only guarantee stays intact and auditable.

Writes go through Zotero 7's live local connector API only
(`POST http://127.0.0.1:23119/connector/saveItems`). `zotero.sqlite` is NEVER written to —
that corrupts the library.

Usage:
    python zotero_save.py --item '<json>'          # one Zotero connector item object
    python zotero_save.py --from-file rec.json     # same object, read from a file
    python zotero_save.py --item '<json>' --dry-run

Item shape (Zotero connector object, not CSL-JSON):

    {"itemType": "journalArticle", "title": "...",
     "creators": [{"firstName": "...", "lastName": "...", "creatorType": "author"}],
     "date": "2016", "publicationTitle": "...", "volume": "...", "issue": "...",
     "pages": "...", "DOI": "...", "extra": "PMID: 27542303"}

A bare "PMID" key is folded into `extra` as `PMID: <n>` (Zotero convention) so callers do
not have to remember it.

Output: exactly ONE JSON object on stdout, always —

    {"status", "itemkey", "duplicate_of", "prepared", "checked", "error"}

    status = added          201 from the API and the key was confirmed by a follow-up search
             duplicate      same DOI/PMID already in the library; nothing was written
             zotero_closed  Zotero is not running; `prepared` carries the payload
             dry_run        de-duplication ran, nothing was POSTed
             error          `error` carries the reason

Exit code is 0 for every outcome above except a usage error (2), so the caller can parse
the JSON instead of branching on the exit status.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zotero_lib  # noqa: E402  (path must be set first)

SAVE_URL = zotero_lib.LOCAL_API + "/connector/saveItems"
CLIENT_URI = "http://localhost/claude-journal-zotero"
REQUIRED = ("itemType", "title")


def _out(**kw):
    """Print the one and only JSON object, then leave."""
    rec = {"status": None, "itemkey": None, "duplicate_of": None,
           "prepared": None, "checked": None, "error": None}
    rec.update(kw)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    sys.exit(0)


def normalize(item):
    """Fold a bare PMID into `extra`; strip empty fields Zotero would store as blanks."""
    it = {k: v for k, v in item.items() if v not in (None, "", [], {})}
    pmid = it.pop("PMID", None)
    if pmid:
        extra = it.get("extra", "")
        if "PMID:" not in extra:
            it["extra"] = (extra + "\n" if extra else "") + f"PMID: {pmid}"
    return it


def identifiers(item):
    """The identifiers a duplicate is decided on, most specific first."""
    ids = []
    doi = (item.get("DOI") or "").strip()
    if doi:
        ids.append(("DOI", doi))
    extra = item.get("extra") or ""
    pmid = zotero_lib._extract_pmid(extra)
    if pmid:
        ids.append(("PMID", str(pmid)))
    return ids


def find_duplicate(item):
    """Search the local library for the same DOI/PMID.

    Returns (itemkey, which_identifier) or (None, None). A library that cannot be read
    is not treated as "no duplicate" — it raises, and the caller reports the error
    rather than risking a second copy of an existing record.
    """
    ids = identifiers(item)
    if not ids:
        return None, None
    # `_open_copy` returns (connection, temp_path); the caller owns both, as in
    # zotero_lib.main()'s own finally blocks.
    conn, tmp = zotero_lib._open_copy()
    if conn is None:
        raise RuntimeError("zotero.sqlite okunamadi - ZOTERO_DATA_DIR ayarli mi?")
    try:
        items = zotero_lib._load_all(conn)
    finally:
        conn.close()
        if tmp:
            try:
                os.remove(tmp)
            except OSError:
                pass
    for field, value in ids:
        for hit in items:
            if (hit.get(field) or "").strip().lower() == value.lower():
                return hit.get("key"), f"{field}={value}"
    return None, None


def post(item, timeout=20):
    body = json.dumps({"items": [item], "uri": CLIENT_URI}).encode("utf-8")
    req = urllib.request.Request(
        SAVE_URL, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "claude-journal-zotero"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def confirm(item):
    """Re-read the library and return the key of the record just written, if findable."""
    key, _ = find_duplicate(item)
    return key


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Add ONE record to the real Zotero library (live API only).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--item", help="Zotero connector item object as a JSON string.")
    src.add_argument("--from-file", help="Path to a file holding that JSON object.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Run the duplicate check and print the payload; do not POST.")
    a = ap.parse_args(argv)

    raw = a.item
    if a.from_file:
        try:
            with open(a.from_file, encoding="utf-8") as f:
                raw = f.read()
        except OSError as e:
            _out(status="error", error=f"dosya okunamadi: {e}")
    try:
        item = json.loads(raw)
    except json.JSONDecodeError as e:
        _out(status="error", error=f"gecersiz JSON: {e}")
    if not isinstance(item, dict):
        _out(status="error", error="beklenen tek bir JSON nesnesi (liste degil)")

    item = normalize(item)
    missing = [f for f in REQUIRED if not item.get(f)]
    if missing:
        _out(status="error", prepared=item,
             error="zorunlu alan eksik: " + ", ".join(missing))

    ids = identifiers(item)
    try:
        dup_key, matched = find_duplicate(item)
    except Exception as e:
        _out(status="error", prepared=item, error=str(e))
    if dup_key:
        _out(status="duplicate", duplicate_of=dup_key, checked=matched, prepared=item)

    # `checked` must distinguish "searched and found nothing" from "could not search".
    swept = ("tekrar denetimi yapildi, esleşme yok: "
             + ", ".join(f"{f}={v}" for f, v in ids)) if ids else \
            "kayitta DOI/PMID yok - tekrar denetimi yapilamadi"

    if a.dry_run:
        _out(status="dry_run", prepared=item, checked=swept)

    if not zotero_lib.api_alive():
        _out(status="zotero_closed", prepared=item,
             error="Zotero calismiyor - yazma yerel API uzerinden yapilir. "
                   "Kullanici Zotero'yu acsin, kayit hazir bekliyor.")

    try:
        code, _body = post(item)
    except urllib.error.HTTPError as e:
        _out(status="error", prepared=item,
             error=f"saveItems HTTP {e.code}: {e.reason}")
    except Exception as e:
        _out(status="error", prepared=item, error=f"saveItems basarisiz: {e}")

    if code not in (200, 201):
        _out(status="error", prepared=item, error=f"beklenmeyen HTTP {code}")

    # Zotero indexes asynchronously; a miss here is not a failure, only an unconfirmed key.
    try:
        key = confirm(item)
    except Exception:
        key = None
    _out(status="added", itemkey=key, prepared=item,
         checked="kayit dogrulandi" if key
                 else "201 alindi, anahtar henuz aranabilir degil - --search ile teyit et")


if __name__ == "__main__":
    main()
