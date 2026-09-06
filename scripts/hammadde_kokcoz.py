#!/usr/bin/env python3
"""Resolve the plugin-journal HOME — the checkout that holds `input/` and `output/`.

Owned by no skill (plugin-root script). Imports no skill module; the skill script
`journalstyle_calismaklasoru.py` imports THIS one to detect the plugin-home mode.
Not a duplicate of that script: `journalstyle_calismaklasoru.py` resolves a STUDY's
workspace (the folder of one .docx); this one resolves the REPO root that holds the
shared `input/` and `output/` folders.

Why this exists: the plugin is installed from GitHub into
`~/.claude/plugins/cache/plugin-journal/journal/<version>/`, and `input/` + `output/`
are git-ignored, so they never reach that copy. `${CLAUDE_PLUGIN_ROOT}` therefore
points at a tree WITHOUT the raw material. The development checkout has to be found
at run time.

Usage:
    python hammadde_kokcoz.py [--no-scaffold] [--quiet]

Resolution order — the first candidate that contains an `input/` directory wins:
    1. env `JOURNAL_PLUGIN_HOME`   (persistent user variable; set once per machine,
                                    reaches only processes started after it was set)
    2. cwd                          (only if `<cwd>/.claude-plugin/plugin.json` says
                                    `"name": "journal"`)
    3. `CLAUDE_PLUGIN_ROOT`, else the parent of this script's folder

Scaffold (default on, idempotent): `output/`, `input/yayinstili/`, `input/authorguidelines/`.
`input/` itself is NEVER created — its presence is what marks the dev checkout; creating
it inside the cache copy would silence the very check this script performs. No README
is written at the root (the plugin's own README.md lives there).

stdout: exactly one JSON object. stderr: info/warnings.
Exit 0 on success; exit 2 with `{"error": "no_input_root", ...}` when no candidate
has `input/` (same contract as `zotero_kutuphaneoku.py` → `no_zotero`).
"""
import argparse
import json
import os
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ENV_VAR = "JOURNAL_PLUGIN_HOME"
HOME_SUBDIRS = ["output", os.path.join("input", "yayinstili"),
                os.path.join("input", "authorguidelines")]


class InputRootNotFound(Exception):
    """Raised by resolve_home() when no candidate carries an `input/` directory."""

    def __init__(self, candidates):
        self.candidates = candidates
        super().__init__("no_input_root")

    def as_json(self):
        return {
            "error": "no_input_root",
            "message": (
                f"No candidate contains an input/ folder. Set {ENV_VAR}=<plugin-journal "
                "checkout root> as a persistent user variable (a value set in Windows reaches "
                "only Claude Code processes started after it) or run from the plugin-journal "
                "checkout. input/ is git-ignored and never reaches the installed cache copy."
            ),
            "candidates": self.candidates,
        }


def _manifest_name(root):
    """Return the `name` in <root>/.claude-plugin/plugin.json, or None."""
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f).get("name")
    except Exception:
        return None


def _candidate(source, path):
    path = os.path.abspath(os.path.expanduser(path))
    return {
        "source": source,
        "path": path,
        "has_input": os.path.isdir(os.path.join(path, "input")),
        "has_manifest": _manifest_name(path) == "journal",
    }


def candidates():
    """All candidates in precedence order (evaluated, not filtered)."""
    out = []
    env = os.environ.get(ENV_VAR)
    if env:
        out.append(_candidate("env:" + ENV_VAR, env))
    cwd = os.getcwd()
    c = _candidate("cwd", cwd)
    if c["has_manifest"]:
        out.append(c)
    else:
        c["has_input"] = False  # a cwd without the manifest never qualifies
        c["skipped"] = "no journal manifest in cwd"
        out.append(c)
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    out.append(_candidate("plugin_root", plugin_root))
    return out


def resolve_home(scaffold=True):
    """Return the resolution dict; raise InputRootNotFound when nothing qualifies."""
    cands = candidates()
    chosen = next((c for c in cands if c["has_input"]), None)
    if chosen is None:
        raise InputRootNotFound(cands)

    home = chosen["path"]
    warnings = []
    if not chosen["has_manifest"]:
        warnings.append(f"{home} has input/ but no .claude-plugin/plugin.json with name 'journal'")

    scaffolded = False
    if scaffold:
        for sub in HOME_SUBDIRS:
            p = os.path.join(home, sub)
            if not os.path.isdir(p):
                os.makedirs(p, exist_ok=True)
                scaffolded = True

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    return {
        "home": home,
        "source": chosen["source"],
        "input_dir": os.path.join(home, "input"),
        "output_dir": os.path.join(home, "output"),
        "yayinstili_dir": os.path.join(home, "input", "yayinstili"),
        "authorguidelines_dir": os.path.join(home, "input", "authorguidelines"),
        "plugin_root": os.path.abspath(plugin_root),
        "scaffolded": scaffolded,
        "candidates": cands,
        "warnings": warnings,
    }


def main():
    ap = argparse.ArgumentParser(description="plugin-journal home (input/ + output/) resolver")
    ap.add_argument("--no-scaffold", action="store_true",
                    help="Only resolve; do not create output/ and input/ subfolders")
    ap.add_argument("--quiet", action="store_true", help="No stderr info lines")
    a = ap.parse_args()
    try:
        result = resolve_home(scaffold=not a.no_scaffold)
    except InputRootNotFound as e:
        print(json.dumps(e.as_json(), ensure_ascii=False, indent=2))
        return 2
    if not a.quiet:
        sys.stderr.write(f"INFO: home={result['home']} (source: {result['source']})\n")
        for w in result["warnings"]:
            sys.stderr.write("WARNING: " + w + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
