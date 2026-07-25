#!/usr/bin/env python3
"""Read the user's real Zotero library — connection layer for the `zotero` skill.

Two backends, auto-selected:

1. **sqlite (primary)** — reads `zotero.sqlite` from the Zotero data directory.
   Works even when the Zotero app is closed. The live file may be locked while
   Zotero runs, so it is always copied to a temp location first and read there.
2. **live local HTTP API (secondary)** — `http://127.0.0.1:23119` when Zotero 7
   is running. Used for freshness checks and (elsewhere) for writing via
   `/connector/saveItems`. This module only *reads*; it never writes to the
   user's library.

Output: JSON to stdout (UTF-8 forced — Windows consoles default to cp1254).
Records are normalized to a CSL-JSON-like shape:

    {"key", "itemType", "title", "creators": [{"family","given","type"}],
     "year", "date", "container-title", "journalAbbreviation", "volume",
     "issue", "pages", "DOI", "PMID", "ISBN", "url", "abstract",
     "collections": [names], "attachments": [absolute pdf paths]}

Usage:
    python zotero_lib.py --list-collections
    python zotero_lib.py --items [--collection KEY_OR_NAME] [--limit N]
    python zotero_lib.py --get ITEMKEY
    python zotero_lib.py --search "terim" [--limit N]
    python zotero_lib.py --status          # which backends are available

Data dir resolution: $ZOTERO_DATA_DIR, else ~/Zotero.
"""
import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import urllib.request

LOCAL_API = "http://127.0.0.1:23119"

# Item types that are containers/noise, not citable records.
_SKIP_TYPES = {"attachment", "note", "annotation"}


# ---------------------------------------------------------------- data dir --

def data_dir():
    d = os.environ.get("ZOTERO_DATA_DIR") or os.path.join(os.path.expanduser("~"), "Zotero")
    return d


def _sqlite_path():
    p = os.path.join(data_dir(), "zotero.sqlite")
    return p if os.path.isfile(p) else None


# ------------------------------------------------------------- live API -----

def api_alive(timeout=2):
    try:
        with urllib.request.urlopen(LOCAL_API + "/connector/ping", timeout=timeout) as r:
            return b"Zotero is running" in r.read()
    except Exception:
        return False


# ------------------------------------------------------------- sqlite -------

def _open_copy():
    """Open a consistent snapshot of zotero.sqlite (the live file may be locked).

    `sqlite3.Connection.backup()` takes a transactionally consistent copy even while
    Zotero is writing; a plain file copy can catch a half-written page and yield a
    torn database. The temp file carries the PID so two runs never collide, and the
    caller removes it (see the `finally` blocks in main()).
    """
    src = _sqlite_path()
    if not src:
        return None, None
    fd, tmp = tempfile.mkstemp(prefix=f"zotero_lib_copy_{os.getpid()}_", suffix=".sqlite")
    os.close(fd)
    dest = None
    try:
        source = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
        try:
            dest = sqlite3.connect(tmp)
            with dest:
                source.backup(dest)
        finally:
            source.close()
    except sqlite3.Error:
        # Zotero'nun kilidi / eski SQLite: dosya kopyasına düş.
        if dest is not None:
            dest.close()
        shutil.copy2(src, tmp)
        dest = sqlite3.connect(tmp)
    dest.row_factory = sqlite3.Row
    return dest, tmp


_PMID_RE = re.compile(r"PMID:?\s*(\d{6,9})", re.IGNORECASE)


def _extract_pmid(extra):
    """Zotero stores PMID inside the free-text `extra` field."""
    if not extra:
        return None
    m = _PMID_RE.search(extra)
    return m.group(1) if m else None


def _year_of(date_str):
    if not date_str:
        return None
    m = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", date_str)
    return m.group(1) if m else None


def _load_all(conn):
    """Load every non-deleted, citable item into normalized dicts."""
    cur = conn.cursor()

    deleted = {r[0] for r in cur.execute("SELECT itemID FROM deletedItems")}

    # field values per item
    fields = {}  # itemID -> {fieldName: value}
    for r in cur.execute(
        "SELECT id.itemID, f.fieldName, v.value "
        "FROM itemData id "
        "JOIN fields f ON f.fieldID = id.fieldID "
        "JOIN itemDataValues v ON v.valueID = id.valueID"
    ):
        fields.setdefault(r[0], {})[r[1]] = r[2]

    # creators per item, ordered
    creators = {}  # itemID -> [ {family, given, type} ]
    for r in cur.execute(
        "SELECT ic.itemID, c.lastName, c.firstName, ct.creatorType, ic.orderIndex "
        "FROM itemCreators ic "
        "JOIN creators c ON c.creatorID = ic.creatorID "
        "JOIN creatorTypes ct ON ct.creatorTypeID = ic.creatorTypeID "
        "ORDER BY ic.itemID, ic.orderIndex"
    ):
        creators.setdefault(r[0], []).append(
            {"family": r[1] or "", "given": r[2] or "", "type": r[3]}
        )

    # collection names per item
    colls = {}  # itemID -> [names]
    for r in cur.execute(
        "SELECT ci.itemID, c.collectionName FROM collectionItems ci "
        "JOIN collections c ON c.collectionID = ci.collectionID"
    ):
        colls.setdefault(r[0], []).append(r[1])

    # attachments: child attachment rows -> absolute storage paths
    atts = {}  # parent itemID -> [abs path]
    storage = os.path.join(data_dir(), "storage")
    for r in cur.execute(
        "SELECT ia.parentItemID, ia.path, i.key "
        "FROM itemAttachments ia JOIN items i ON i.itemID = ia.itemID "
        "WHERE ia.parentItemID IS NOT NULL AND ia.path IS NOT NULL"
    ):
        parent, path, key = r[0], r[1], r[2]
        if path.startswith("storage:"):
            p = os.path.join(storage, key, path[len("storage:"):])
        else:
            p = path  # linked file, already absolute
        atts.setdefault(parent, []).append(p)

    items = []
    for r in cur.execute(
        "SELECT i.itemID, i.key, t.typeName FROM items i "
        "JOIN itemTypes t ON t.itemTypeID = i.itemTypeID"
    ):
        item_id, key, type_name = r[0], r[1], r[2]
        if item_id in deleted or type_name in _SKIP_TYPES:
            continue
        f = fields.get(item_id, {})
        rec = {
            "key": key,
            "itemType": type_name,
            "title": f.get("title"),
            "creators": creators.get(item_id, []),
            "date": f.get("date"),
            "year": _year_of(f.get("date")),
            "container-title": f.get("publicationTitle") or f.get("bookTitle")
                               or f.get("proceedingsTitle"),
            "journalAbbreviation": f.get("journalAbbreviation"),
            "volume": f.get("volume"),
            "issue": f.get("issue"),
            "pages": f.get("pages"),
            "DOI": f.get("DOI"),
            "PMID": _extract_pmid(f.get("extra")),
            "ISBN": f.get("ISBN"),
            "url": f.get("url"),
            "abstract": (f.get("abstractNote") or "")[:400] or None,
            "collections": colls.get(item_id, []),
            "attachments": atts.get(item_id, []),
        }
        items.append(rec)
    return items


def _list_collections(conn):
    cur = conn.cursor()
    deleted = {r[0] for r in cur.execute("SELECT collectionID FROM deletedCollections")}
    counts = {}
    for r in cur.execute("SELECT collectionID, COUNT(*) FROM collectionItems GROUP BY collectionID"):
        counts[r[0]] = r[1]
    out = []
    for r in cur.execute(
        "SELECT collectionID, collectionName, key, parentCollectionID FROM collections"
    ):
        if r[0] in deleted:
            continue
        out.append({"key": r[2], "name": r[1], "parent": r[3], "itemCount": counts.get(r[0], 0)})
    return out


def _account_info(conn):
    """Account identifiers from the settings table (for Zotero field URIs)."""
    info = {"user_id": None, "local_user_key": None, "username": None}
    try:
        cur = conn.cursor()
        for r in cur.execute(
            "SELECT key, value FROM settings WHERE setting = 'account'"
        ):
            k, v = r[0], r[1]
            if k == "userID":
                info["user_id"] = str(v)
            elif k == "localUserKey":
                info["local_user_key"] = str(v)
            elif k == "username":
                info["username"] = str(v)
    except sqlite3.Error:
        pass
    return info


# ------------------------------------------------------------- commands -----

def _match_collection(items, wanted):
    """Filter by collection key or (case-insensitive) name."""
    wl = wanted.lower()
    return [it for it in items if any(wl == c.lower() for c in it["collections"]) or wanted in it.get("collections", [])]


def _search_items(items, term):
    tl = term.lower()
    hits = []
    for it in items:
        hay = " ".join(filter(None, [
            it.get("title"), it.get("container-title"), it.get("DOI"),
            it.get("PMID"), it.get("year"), it.get("abstract"),
            " ".join(c["family"] + " " + c["given"] for c in it["creators"]),
        ])).lower()
        if tl in hay:
            hits.append(it)
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read the local Zotero library.")
    ap.add_argument("--list-collections", action="store_true")
    ap.add_argument("--items", action="store_true")
    ap.add_argument("--collection", help="Collection key or name filter (with --items).")
    ap.add_argument("--get", metavar="ITEMKEY", help="Dump one item by its key.")
    ap.add_argument("--search", metavar="TERM", help="Search title/authors/journal/DOI/PMID/abstract.")
    ap.add_argument("--limit", type=int, default=0, help="Max records to print (0 = all).")
    ap.add_argument("--status", action="store_true", help="Report backend availability.")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if args.status:
        status = {
            "data_dir": data_dir(),
            "sqlite": _sqlite_path() is not None,
            "live_api": api_alive(),
        }
        # account identifiers (needed for Zotero field URIs in zotero_cite.py)
        conn, tmp = _open_copy()
        if conn is not None:
            try:
                status["account"] = _account_info(conn)
            finally:
                conn.close()
                try:
                    os.remove(tmp)
                except OSError:
                    pass
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0

    conn, tmp = _open_copy()
    if conn is None:
        print(json.dumps({
            "error": "no_zotero",
            "message": f"zotero.sqlite bulunamadı: {os.path.join(data_dir(), 'zotero.sqlite')}. "
                       "ZOTERO_DATA_DIR ortam değişkenini ayarlayın veya Zotero kurun.",
        }, ensure_ascii=False))
        return 0

    try:
        if args.list_collections:
            result = _list_collections(conn)
        else:
            items = _load_all(conn)
            if args.get:
                result = [it for it in items if it["key"] == args.get]
                if not result:
                    result = {"error": "not_found", "key": args.get}
            elif args.search:
                result = _search_items(items, args.search)
            else:  # --items (default listing)
                result = items
                if args.collection:
                    result = _match_collection(result, args.collection)
        if isinstance(result, list) and args.limit > 0:
            result = result[:args.limit]
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        conn.close()
        try:
            os.remove(tmp)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
