#!/usr/bin/env python3
"""Stamp each job folder's name with its last update: `20261004 2152 Tez C2` (1.30.0).

Owned by no skill (plugin-root script). User rule, 2026-10-04: every job folder — and every
folder the user made inside `input/<job>/` — starts with the `YYYYMMDD HHMM` of the newest file
beneath it, and that stamp follows the work automatically. Run by the plugin's Stop hook
(`hooks/hooks.json`, `--hook`) after every turn, and by hand.

What is renamed:
    input/<job>/                 every folder except `authorguidelines/`, `yayinstili/`, dot folders
    input/<job>/<sub>/           user subfolders, except `research/`, `referanslar/`, `yedekler/`
    output/<job>/                a folder whose identity matches an input job (extension folders
                                 like `docx/`, `png/` never match, so they are left alone)
Nothing inside `output/<job>/` is renamed (`yedekler/`, poster packages keep their names).

The stamp is the newest file mtime beneath the folder (`~$…` / `.~lock…` ignored); an empty
folder keeps its name. A folder is skipped — and retried on the next run — when a file in it
changed within the last 120 s (a writer may still be at work), when the rename fails (a file is
open in Word: `kilitli`), or when the target name already exists. The job's identity is the name
without the stamp (`cikti_yolcoz.damga_ayir`); scripts find a job by identity, never by stamp.

Usage:
    python isklasoru_addamgala.py [--kuru] [--hook]
stdout: one JSON {home, kuru, yeniden_adlandirilan: [[old, new]], atlanan: [{yol, neden}]}.
`--hook`: no stdout, never fails (exit 0), writes `output/.isklasoru_damga_son.json` as the
run's artefact. Without a checkout (`no_input_root`) it does nothing.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cikti_yolcoz import damga, damga_ayir  # noqa: E402
from hammadde_kokcoz import resolve_home, InputRootNotFound  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SABIT_KOK = {"authorguidelines", "yayinstili"}
KORUNAN_ALT = {"research", "referanslar", "yedekler"}
SESSIZLIK_SN = 120
SON_DOSYA = ".isklasoru_damga_son.json"


def _sayilmaz(ad):
    return ad.startswith("~$") or ad.startswith(".~lock")


def en_yeni(klasor):
    """Newest file mtime beneath `klasor`, or None when it holds no file."""
    en = None
    for kok, _, dosyalar in os.walk(klasor):
        for d in dosyalar:
            if _sayilmaz(d):
                continue
            try:
                t = os.path.getmtime(os.path.join(kok, d))
            except OSError:
                continue
            en = t if en is None or t > en else en
    return en


def _alt_klasorler(kok, haric):
    try:
        adlar = sorted(os.listdir(kok))
    except OSError:
        return []
    return [os.path.join(kok, a) for a in adlar
            if os.path.isdir(os.path.join(kok, a)) and not a.startswith(".")
            and damga_ayir(a)[1].casefold() not in haric]


def adaylar(home):
    """Folders to stamp, children before their parent (a parent rename moves the children)."""
    giris, cikis = home["input_dir"], home["output_dir"]
    out, kimlikler = [], set()
    for isk in _alt_klasorler(giris, SABIT_KOK):
        out.extend(_alt_klasorler(isk, KORUNAN_ALT))
        out.append(isk)
        kimlikler.add(damga_ayir(os.path.basename(isk))[1].casefold())
    for isk in _alt_klasorler(cikis, set()):
        if damga_ayir(os.path.basename(isk))[1].casefold() in kimlikler:
            out.append(isk)
    return out


def damgala(home, kuru=False, simdi=None):
    simdi = simdi or time.time()
    yapilan, atlanan = [], []
    for k in adaylar(home):
        t = en_yeni(k)
        if t is None:
            continue
        ad = os.path.basename(k)
        yeni_ad = f"{damga(datetime.fromtimestamp(t))} {damga_ayir(ad)[1]}"
        if yeni_ad == ad:
            continue
        if simdi - t < SESSIZLIK_SN:
            atlanan.append({"yol": k, "neden": "yeni_yazim"})
            continue
        hedef = os.path.join(os.path.dirname(k), yeni_ad)
        if os.path.exists(hedef):
            atlanan.append({"yol": k, "neden": "hedef_var"})
            continue
        if not kuru:
            try:
                os.rename(k, hedef)
            except OSError as exc:
                atlanan.append({"yol": k, "neden": "kilitli", "hata": str(exc)})
                continue
        yapilan.append([k, hedef])
    return {"home": home["home"], "kuru": kuru, "zaman": damga(),
            "yeniden_adlandirilan": yapilan, "atlanan": atlanan}


def main(argv=None):
    ap = argparse.ArgumentParser(description="stamp job folders with their last update")
    ap.add_argument("--kuru", action="store_true", help="list only, rename nothing")
    ap.add_argument("--hook", action="store_true", help="Stop-hook mode: silent, always exit 0")
    a = ap.parse_args(argv)
    try:
        home = resolve_home(scaffold=False)
    except InputRootNotFound as e:
        if a.hook:
            return 0
        print(json.dumps(e.as_json(), ensure_ascii=False, indent=1))
        return 2
    if a.hook:
        try:
            sonuc = damgala(home)
            with open(os.path.join(home["output_dir"], SON_DOSYA), "w", encoding="utf-8") as f:
                json.dump(sonuc, f, ensure_ascii=False, indent=1)
        except Exception:
            pass
        return 0
    print(json.dumps(damgala(home, kuru=a.kuru), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
